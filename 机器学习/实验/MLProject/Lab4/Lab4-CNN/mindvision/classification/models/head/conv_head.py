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
"""Convolution head."""

from mindspore import nn

from mindvision.engine.class_factory import ClassFactory, ModuleType


@ClassFactory.register(ModuleType.HEAD)
class ConvHead(nn.Cell):
    """
    ConvHead architecture.

    Args:
        input_channel (int) – The number of input channels.
        num_classes (int): Number of classes.
        has_bias (bool) – Specifies whether the layer uses a bias vector. Default: True.

    Returns:
        Tensor, output tensor.
    """

    def __init__(self,
                 input_channel: int,
                 num_classes: int,
                 has_bias: bool = True
                 ) -> None:
        super(ConvHead, self).__init__()

        self.classifier = nn.Conv2d(input_channel, num_classes, kernel_size=1, stride=1, has_bias=has_bias)
        self.flatten = nn.Flatten()

    def construct(self, x):
        x = self.classifier(x)
        x = self.flatten(x)

        return x
