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
# ============================================================================
""" MindSpore Vision Classification export script. """

import numpy as np

import mindspore as ms
from mindspore import Tensor, context, load_checkpoint, load_param_into_net, export

from mindvision.classification.models.builder import build_classifier
from mindvision.engine.utils.config import Config, parse_args


def main(pargs):
    config = Config(pargs.config)

    # set config context
    context.set_context(**config.context)

    # set network
    network = build_classifier(config.model)

    # load pertain model
    param_dict = load_checkpoint(config.export.pretrained_model)
    load_param_into_net(network, param_dict)

    # export network
    inputs = Tensor(np.ones([config.export.batch_size,
                             config.export.input_channel,
                             config.export.image_height,
                             config.export.image_width]),
                    ms.float32)
    export(network, inputs, file_name=config.export.file_name,
           file_format=config.export.file_formate)

    print("=" * 80)
    print(f"[End of export `{config.model_name}`]")


if __name__ == '__main__':
    args = parse_args()
    main(args)
