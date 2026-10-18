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
""" MobileNetV2 backbone."""

from typing import Optional, List

from mindspore import nn
from mindspore.ops.operations import Add

from mindvision.classification.models.blocks import ConvNormActivation
from mindvision.classification.models.utils import make_divisible
from mindvision.engine.class_factory import ClassFactory, ModuleType


class InvertedResidual(nn.Cell):
    """
    Mobilenetv2 residual block definition.

    Args:
        in_channel (int): Input channel.
        out_channel (int): Output channel.
        stride (int): Stride size for the first convolutional layer. Default: 1.
        expand_ratio (int): expand ration of input channel.
        norm (nn.Cell, optional): Norm layer that will be stacked on top of the convoution
        layer. Default: None.
    Returns:
        Tensor, output tensor.

    Examples:
        >>> InvertedResidual(3, 256, 1, 1)
    """

    def __init__(self,
                 in_channel: int,
                 out_channel: int,
                 stride: int,
                 expand_ratio: int,
                 norm: Optional[nn.Cell] = None
                 ) -> None:
        super(InvertedResidual, self).__init__()
        assert stride in [1, 2]

        if not norm:
            norm = nn.BatchNorm2d

        hidden_dim = round(in_channel * expand_ratio)
        self.use_res_connect = stride == 1 and in_channel == out_channel

        layers: List[nn.Cell] = []
        if expand_ratio != 1:
            # pw
            layers.append(
                ConvNormActivation(in_channel, hidden_dim, kernel_size=1, norm=norm, activation=nn.ReLU6)
            )
        layers.extend([
            # dw
            ConvNormActivation(
                hidden_dim,
                hidden_dim,
                stride=stride,
                groups=hidden_dim,
                norm=norm,
                activation=nn.ReLU6
            ),
            # pw-linear
            nn.Conv2d(hidden_dim, out_channel, kernel_size=1,
                      stride=1, has_bias=False),
            norm(out_channel)
        ])
        self.conv = nn.SequentialCell(layers)
        self.add = Add()

    def construct(self, x):
        identity = x
        x = self.conv(x)
        if self.use_res_connect:
            return self.add(identity, x)
        return x


@ClassFactory.register(ModuleType.BACKBONE)
class MobileNetV2(nn.Cell):
    """
    MobileNetV2 architecture.

    Args:
        alpha (int): Channels multiplier for round to 8/16 and others. Default is 1.0.
        inverted_residual_setting (list): Inverted residual settings. Default is None.
        round_nearest (int): Round the number of channels in each layer to be a multiple of this number
        set to 1 to turn off rounding. Default is 8.
        block (nn.Cell, optional): Module specifying inverted residual building block for mobilenet. Default: None.
        norm (nn.Cell, optional): Norm layer that will be stacked on top of the convoution
        layer. Default: None.
    Returns:
        Tensor, output tensor.

    Examples:
        >>> MobileNetV2(**kwargs)
    """

    def __init__(self,
                 alpha: float = 1.0,
                 inverted_residual_setting: Optional[List[List[int]]] = None,
                 round_nearest: int = 8,
                 block: Optional[nn.Cell] = None,
                 norm: Optional[nn.Cell] = None,
                 ) -> None:
        super(MobileNetV2, self).__init__()

        if not block:
            block = InvertedResidual
        if not norm:
            norm = nn.BatchNorm2d

        input_channel = make_divisible(32 * alpha, round_nearest)
        last_channel = make_divisible(1280 * max(1.0, alpha), round_nearest)

        # Setting of inverted residual blocks.
        if not inverted_residual_setting:
            inverted_residual_setting = [
                # t, c, n, s
                [1, 16, 1, 1],
                [6, 24, 2, 2],
                [6, 32, 3, 2],
                [6, 64, 4, 2],
                [6, 96, 3, 1],
                [6, 160, 3, 2],
                [6, 320, 1, 1],
            ]

        # Building first layer.
        features: List[nn.Cell] = [
            ConvNormActivation(3, input_channel, stride=2, norm=norm, activation=nn.ReLU6)
        ]

        # Building inverted residual blocks.
        # t: The expansion factor.
        # c: Number of output channel.
        # n: Number of block.
        # s: First block stride.
        for t, c, n, s in inverted_residual_setting:
            output_channel = make_divisible(c * alpha, round_nearest)
            for i in range(n):
                stride = s if i == 0 else 1
                features.append(block(input_channel, output_channel, stride, expand_ratio=t, norm=norm))
                input_channel = output_channel

        # Building last several layers.
        features.append(
            ConvNormActivation(input_channel, last_channel, kernel_size=1, norm=norm, activation=nn.ReLU6)
        )
        # Make it nn.CellList.
        self.features = nn.SequentialCell(features)

    def construct(self, x):
        x = self.features(x)
        return x
