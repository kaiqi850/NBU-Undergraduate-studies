# -*- coding: utf-8 -*-

# Copyright 2021 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""the module is used to train model."""

import argparse
import datetime
import os

import mindspore.common.dtype as mstype
from mindspore import Tensor
from mindspore import context, Model, set_seed
from mindspore.communication import init, get_rank, get_group_size
from mindspore.context import ParallelMode
from mindspore.profiler import Profiler
from mindspore.train.callback import TimeMonitor, RunContext, CheckpointConfig, \
    ModelCheckpoint

from mindvision.detection.models.builder import build_detector, build_train_wrapper
from mindvision.detection.models.utils.custom_op import network_convert_type
from mindvision.detection.utils.loss_callback import LossCallBack
from mindvision.engine.dataset.dataloader import build_dataloader
from mindvision.engine.lr_schedule.lr_schedule import get_lr
from mindvision.engine.optimizer.builder import build_optimizer
from mindvision.engine.utils.config import Config, ActionDict
from mindvision.log import info


def parse_arguments():
    """parse train arguments"""
    parser = argparse.ArgumentParser(description='Train a detector')
    parser.add_argument("--data_url", type=str, default="", help="Dataset path for train on ModelArts platform")
    parser.add_argument("--train_url", type=str, default="", help="Train file outputs path on ModelArts platform")
    parser.add_argument("--train_data", type=str, default="", help="Train file inputs path on ModelArts platform")
    parser.add_argument('--is_modelarts', type=bool, default=False, help='Whether to run on the modelarts platform')
    parser.add_argument('--config', type=str, default="", help='train config file path')
    parser.add_argument('--work_dir', default='./',
                        help='the path to save logs and models')
    parser.add_argument("--device_id", type=int, default=0, help="Device id, default is 0.")
    parser.add_argument('--seed', default=1, help='the random seed')
    parser.add_argument(
        '--options',
        nargs='+',
        action=ActionDict,
        help='override some settings in the used config, the key-value pair'
             'in xxx=yyy format will be merged into config file')

    args = parser.parse_args()
    return args


def init_cfg(in_args, in_cfg):
    """Init Train Config."""
    # create work path
    if not os.path.isdir(in_args.work_dir):
        os.makedirs(in_args.work_dir)

    # init logger
    in_cfg.outputs_dir = os.path.join(in_args.work_dir,
                                      in_cfg.ckpt_path,
                                      datetime.datetime.now().
                                      strftime('%Y-%m-%d_time_%H_%M_%S'))

    # init context
    if in_args.device_id:
        in_cfg.context.device_id = int(in_args.device_id)
    context.set_context(**in_cfg.context)

    # init distributed
    if in_cfg.is_distributed:
        if in_cfg.context.device_target == "Ascend":
            init()
        else:
            init("nccl")
        in_cfg.rank = get_rank()
        in_cfg.group_size = get_group_size()
    else:
        in_cfg.parallel.parallel_mode = ParallelMode.STAND_ALONE
    context.reset_auto_parallel_context()
    if in_cfg.is_distributed:
        in_cfg.parallel.device_num = get_group_size()
    context.set_auto_parallel_context(**in_cfg.parallel)

    # init profiler
    in_cfg.profiler.outputs_dir = in_cfg.outputs_dir
    if in_cfg.need_profiler:
        profiler = Profiler(**in_cfg.profiler)
    else:
        profiler = None
    return in_cfg, profiler


def main():
    args = parse_arguments()
    set_seed(args.seed)
    cfg = Config(args.config)
    if args.options is not None:
        cfg.merge_from_dict(args.options)
    train_cfg = cfg.train

    # if the code runs in ModelArts, copy train dataset to ModelArts Training Workspace
    if args.is_modelarts:
        import moxing as mox

        if not os.path.exists(args.train_data):
            os.makedirs(args.train_data)
        mox.file.copy_parallel(args.data_url, args.train_data)

    # init train_cfg
    train_cfg, profiler = init_cfg(args, train_cfg)

    # create model
    network = build_detector(cfg.model)
    network.set_train(True)

    # init weights
    if os.path.exists(train_cfg.load_path):
        info('Find Full-Network Loaded.')
        network.init_weights(train_cfg.load_path)
    elif os.path.exists(train_cfg.backbone_path):
        info('Only Load Backbone Weights.')
        network.init_backbone(train_cfg.backbone_path)
    else:
        info('Not Load Any Weights.')
    network_convert_type(network, train_cfg.network_data_type)
    info('Finish get network')

    # create dataset
    if train_cfg.is_distributed:
        cfg.data_loader.train.dataset.shard_id = get_rank()
        cfg.data_loader.train.dataset.num_shards = get_group_size()
    data_loader = build_dataloader(cfg.data_loader, types='train')
    ds = data_loader()
    data_size = ds.get_dataset_size()
    info('Finish loading dataset, data_size:{}'.format(data_size))

    # init lr
    lr_cfg = cfg.learning_rate
    lr_cfg.steps_per_epoch = int(ds.get_dataset_size())
    lr = get_lr(lr_cfg)
    lr = Tensor(lr, mstype.float32)

    # init optimizer
    cfg.optimizer.params = network.get_trainable_params()
    cfg.optimizer.learning_rate = lr
    opt = build_optimizer(cfg.optimizer)

    # init train wrapper
    if cfg.model.config.use_global_norm:
        loss_scale = 1024.0
        default_args = {'network': network, 'optimizer': opt, 'sens': loss_scale}
    else:
        loss_scale = cfg.optimizer.loss_scale
        default_args = {'network': network, 'optimizer': opt, 'sens': loss_scale // 2}
    train_wrapper = build_train_wrapper(cfg.train_wrapper, default_args)
    network = train_wrapper.get_network()
    info('Finish building train wrapper')

    # init callbacks
    time_cb = TimeMonitor(data_size=ds.get_dataset_size())
    loss_cb = LossCallBack(save_path=args.work_dir, rank_id=0)
    cb = [time_cb, loss_cb]

    if train_cfg.ckpt_interval <= 0:
        train_cfg.ckpt_interval = lr_cfg.steps_per_epoch

    if train_cfg.rank_save_ckpt_flag:
        cb_params = Config()
        cb_params.train_network = network
        cb_params.epoch_num = train_cfg.max_epoch * lr_cfg.steps_per_epoch // train_cfg.ckpt_interval
        cb_params.cur_epoch_num = 1
        run_context = RunContext(cb_params)
        # checkpoint save
        if train_cfg.ckpt is not None and train_cfg.ckpt.max_num is not None:
            ckpt_max_num = train_cfg.ckpt.max_num
        else:
            ckpt_max_num = 10
        ckpt_config = CheckpointConfig(
            save_checkpoint_steps=train_cfg.ckpt_interval,
            keep_checkpoint_max=ckpt_max_num)
        save_ckpt_path = os.path.join(train_cfg.outputs_dir,
                                      'ckpt_' + str(train_cfg.rank) + '/')
        ckpt_cb = ModelCheckpoint(config=ckpt_config,
                                  directory=save_ckpt_path,
                                  prefix='{}'.format(train_cfg.rank))
        ckpt_cb.begin(run_context)
        cb.append(ckpt_cb)

    # train model
    model = Model(network)
    if train_cfg.dataset_sink_mode is None:
        dataset_sink_mode = False
    else:
        dataset_sink_mode = train_cfg.dataset_sink_mode

    model.train(train_cfg.max_epoch, ds, callbacks=cb, dataset_sink_mode=dataset_sink_mode)

    if train_cfg.need_profiler and profiler is not None:
        profiler.analyse()

    # Apply for ModelArts Training output and save files config
    if args.is_modelarts:
        end_file_name = args.work_dir.split('/')[-1]
        obs_work_path = os.path.join(args.train_url, end_file_name)
        if not mox.file.exists(obs_work_path):
            mox.file.make_dirs(obs_work_path)
        mox.file.copy_parallel(args.work_dir, obs_work_path)

if __name__ == '__main__':
    main()
