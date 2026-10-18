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
"""Convert resnet pretrained model to faster-rcnn backbone pretrained model."""

import argparse
import os

import mindspore.common.dtype as mstype
from mindspore.common.parameter import Parameter
from mindspore.common.tensor import Tensor
from mindspore.train.serialization import load_checkpoint, save_checkpoint


def convert_weights(load_path, ver="v2"):
    """Convert resnetv2 pretrained model to faster-rcnn backbonev2 pretrained model."""
    ms_ckpt = load_checkpoint(load_path)
    weights = {}
    for ms_name in ms_ckpt:
        if ms_name.startswith("layer") or ms_name.startswith("conv1") or ms_name.startswith("bn"):
            param_name = "backbone." + ms_name
        else:
            param_name = ms_name
        if ver == "v1":
            # model_zoo resnet to faster-rcnn backbonev1
            if "down_sample_layer.0" in param_name:
                param_name = param_name.replace("down_sample_layer.0", "conv_down_sample")
            if "down_sample_layer.1" in param_name:
                param_name = param_name.replace("down_sample_layer.1", "bn_down_sample")
        if ver == "v3":
            # model_zoo resnext to faster-rcnn backbonev2
            if "down_sample.conv" in param_name:
                param_name = param_name.replace("down_sample.conv", "down_sample_layer.0")
            if "down_sample.bn" in param_name:
                param_name = param_name.replace("down_sample.bn", "down_sample_layer.1")
            if "backbone.conv.weight" in param_name:
                param_name = param_name.replace("backbone.conv.weight", "backbone.conv1.weight")
            if "backbone.bn" in param_name:
                param_name = param_name.replace("backbone.bn", "backbone.bn1")

        weights[param_name] = ms_ckpt[ms_name].data.asnumpy()

    parameter_dict = {}
    for name in weights:
        parameter_dict[name] = Parameter(Tensor(weights[name], mstype.float32), name=name)

    param_list = []
    for key, value in parameter_dict.items():
        param_list.append({"name": key, "data": value})

    return param_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert resnet weights to adapt faster-rcnn')
    parser.add_argument("--model_zoo", type=str,
                        default="resnet50_ascend_v130_imagenet2012_official_cv_bs256_top1acc76.97__top5acc_93.44.ckpt",
                        help="pretrained model in Mindspore-Model-Zoo")
    parser.add_argument("--save_path", type=str, default="pretrained",
                        help="Save pretrained model after converting it.")
    parser.add_argument("--model_name", type=str, default="backbone_resnet50",
                        help="To save pretrained model name.")
    parser.add_argument("--version", type=str, default="v1",
                        help="ResNet class is ResNet(V1) or ResNetV2(V2) or ResNeXt(V3).")
    args = parser.parse_args()

    save_path = args.save_path
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    model_name = args.model_name
    ckpt_file = args.model_zoo
    version = args.version

    parameter_list = convert_weights(ckpt_file, version)
    save_checkpoint(parameter_list, os.path.join(save_path, model_name))
