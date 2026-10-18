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
"""the module is used to predict image."""

import argparse
import datetime
import json
import os
import time

import mindspore.common.dtype as mstype
import numpy as np
from mindspore import context, set_seed
from mindspore.train.serialization import load_checkpoint, load_param_into_net

from mindvision.detection.models.builder import build_detector
from mindvision.detection.utils.vision import img2vision
from mindvision.engine.dataset.dataloader import build_dataloader
from mindvision.engine.utils.config import Config, ActionDict
from mindvision.log import info


def parse_arguments():
    """parse eval arguments"""
    parser = argparse.ArgumentParser(description="prediction")
    parser.add_argument("--save_dir", type=str, default="", help="File path for save detect result")
    parser.add_argument("--img_show", type=bool, default=True, help="Show the result for this picture")
    parser.add_argument('--config', help='config file path')
    parser.add_argument("--checkpoint_path", type=str, required=True, help="Checkpoint file path.")
    parser.add_argument('--work_dir', default='outputs', help='the path to save logs and models')
    parser.add_argument("--device_target", type=str, default="Ascend",
                        help="device where the code will be implemented, default is Ascend")
    parser.add_argument("--device_id", type=int, default=5, help="Device id, default is 0.")
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

    # create work path
    if args.work_dir:
        eval_cfg.work_dir = args.work_dir

    if not os.path.exists(eval_cfg.work_dir):
        os.makedirs(eval_cfg.work_dir)

    # init logger
    eval_cfg.outputs_dir = os.path.join(eval_cfg.work_dir,
                                        datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S'))

    # init context
    if args.device_id:
        eval_cfg.context.device_id = int(args.device_id)
    context.set_context(**eval_cfg.context)

    # create model
    network = build_detector(cfg.model)
    network.set_train(False)
    info('Finish build network')

    network.to_float(mstype.float16)

    # load model parameters to network
    if args.checkpoint_path:
        eval_cfg.ckpt_path = args.checkpoint_path

    param_dict = load_checkpoint(eval_cfg.ckpt_path)
    load_param_into_net(network, param_dict)

    # Load image for prediction. TODO: change the arguments.
    data_loader = build_dataloader(cfg.data_loader, False, True)  # pylint: disable-msg=too-many-arguments
    ds = data_loader()
    data_size = ds.get_dataset_size()
    info('Finish loading dataset, data_size: {}'.format(data_size))

    # Use model to predict this picture
    img_show = args.img_show
    save_dir = os.path.join(args.work_dir, args.save_dir)

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Fetch Detection Pictures Information
    root_cfg = cfg.data_loader.infer
    id_to_img_path = root_cfg.prefix
    with open(id_to_img_path, 'r') as f:
        img_path_dict = json.load(f)

    # Starting predict pictures
    for data in ds.create_dict_iterator():

        img_data = data['image']
        img_metas = data['image_shape']
        img_id = data["image_id"]
        start = time.time()
        outputs = network(img_data, img_metas)
        end = time.time()

        for j in range(eval_cfg.test_batch_size):
            print("Processing {}\ncost time {}".format(img_path_dict[str(img_id[j])], end - start))
            bboxes = np.squeeze(outputs[0][j].asnumpy())
            labels = np.squeeze(outputs[1][j].asnumpy())
            masks = np.squeeze(outputs[2][j].asnumpy())
            if img_show:
                img2vision(img_path_dict[str(img_id[j])], save_dir, bboxes, labels, masks)


if __name__ == "__main__":
    main()
