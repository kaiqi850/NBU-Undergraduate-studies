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
"""main func to eval model."""

import argparse
import datetime
import os
import time

from mindspore import context, set_seed
from mindspore.train.serialization import load_checkpoint, load_param_into_net

from mindvision.detection.models.builder import build_detector, build_detection_engine
from mindvision.detection.models.utils.custom_op import network_convert_type
from mindvision.engine.dataset.dataloader import build_dataloader
from mindvision.engine.utils.config import Config, ActionDict
from mindvision.log import info


def parse_arguments():
    """parse eval arguments"""
    parser = argparse.ArgumentParser(description="evaluation")
    parser.add_argument("--data_url", type=str, default="", help="Dataset path for train on ModelArts platform")
    parser.add_argument("--eval_url", type=str, default="", help="Eval file outputs path on ModelArts platform")
    parser.add_argument("--eval_data", type=str, default="", help="Eval file inputs path on ModelArts platform")
    parser.add_argument('--is_modelarts', type=bool, default=False, help='Whether to run on the modelarts platform')
    parser.add_argument('--config', help='config file path')
    parser.add_argument("--ann_file", type=str, default="", help="Ann file, default is val.json.")
    parser.add_argument("--checkpoint_path", type=str, required=True, help="Checkpoint file path.")
    parser.add_argument('--work_dir', default='./', help='the path to save logs and models')
    parser.add_argument("--device_target", type=str, default="Ascend",
                        help="device where the code will be implemented, default is Ascend")
    parser.add_argument("--device_id", type=int, default=4, help="Device id, default is 0.")
    parser.add_argument('--seed', default=1, help='the random seed')
    parser.add_argument(
        '--options',
        nargs='+',
        action=ActionDict,
        help='override some settings in the used config, the key-value pair'
             'in xxx=yyy format will be merged into config file')
    args_opt = parser.parse_args()
    return args_opt


def main():
    args = parse_arguments()
    set_seed(args.seed)

    cfg = Config(args.config)
    if args.options is not None:
        cfg.merge_from_dict(args.options)
    eval_cfg = cfg.eval

    # if the code runs in ModelArts, copy train dataset to ModelArts Training Workspace
    if args.is_modelarts:
        import moxing as mox

        if not os.path.exists(args.eval_data):
            os.makedirs(args.eval_data)
        mox.file.copy_parallel(args.data_url, args.eval_data)

    # create work path
    if not os.path.isdir(args.work_dir):
        os.makedirs(args.work_dir)

    # init logger
    eval_cfg.outputs_dir = os.path.join(args.work_dir,
                                        eval_cfg.ckpt_path,
                                        datetime.datetime.now().
                                        strftime('%Y-%m-%d_%H_%M_%S'))

    # init context
    if args.device_id:
        eval_cfg.context.device_id = int(args.device_id)
    context.set_context(**eval_cfg.context)

    # create model
    cfg.model.backbone.weights_update = False
    network = build_detector(cfg.model)
    network.set_train(False)
    info('Finish build network')

    # create dataset
    data_loader = build_dataloader(cfg.data_loader, 'eval')
    ds = data_loader()
    data_size = ds.get_dataset_size()
    info('Finish loading dataset, data_size: {}'.format(data_size))

    # load model
    if args.checkpoint_path:
        eval_cfg.ckpt_path = args.checkpoint_path
    if args.ann_file:
        eval_cfg.ann_file = args.ann_file

    param_dict = load_checkpoint(eval_cfg.ckpt_path)
    load_param_into_net(network, param_dict)
    network_convert_type(network, eval_cfg.network_data_type)
    # create detection_engine
    detection = build_detection_engine(eval_cfg.detection_engine)
    # Starting predict pictures
    do_eval(ds, network, detection)

    detection.get_eval_result()


def do_eval(dataset, network, detection):
    """Do evaluation."""
    eval_iter = 0
    print("\n========================================\n")
    print("Total images num: ", dataset.get_dataset_size())
    print("Processing, please wait a moment.")
    for data in dataset.create_dict_iterator(num_epochs=1):
        eval_iter = eval_iter + 1
        data_tuple = data.values()
        start = time.time()
        output = network(*data_tuple)
        end = time.time()
        print("Iter {} cost time {}".format(eval_iter, end - start))

        detection.detect(output, **data)


if __name__ == '__main__':
    main()
