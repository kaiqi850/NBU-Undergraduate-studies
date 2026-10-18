# Copyright 2022 Huawei Technologies Co., Ltd
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
"""EfficientNet Architecture."""

import math
import copy
from functools import partial
from typing import List, Optional, Callable

import mindspore.nn as nn
from mindspore import Tensor
from mindspore.ops import operations as P

from mindvision.check_param import Validator, Rel
from mindvision.classification.models.utils import make_divisible
from mindvision.engine.class_factory import ClassFactory, ModuleType
from mindvision.classification.models.blocks import ConvNormActivation, SqueezeExcite, DropConnect, Swish

__all__ = [
    'MBConvConfig',
    'MBConv',
    'EfficientNet',  # registration mechanism to use yaml configuration
]


class MBConvConfig:
    """
    The Parameters of MBConv which need to multiply the expand_ration.

    Args:
        expand_ratio (float): The Times of the num of out_channels with respect to in_channels.
        kernel_size (int): The kernel size of the depthwise conv.
        stride (int): The stride of the depthwise conv.
        in_chs (int): The input_channels of the MBConv Module.
        out_chs (int): The output_channels of the MBConv Module.
        num_layers (int): The num of MBConv Module.
        width_cnf: The ratio of the channel.
        depth_cnf: The ratio of num_layers.

    Returns:
        None

    Examples:
        >>> cnf = MBConvConfig(1, 3, 1, 32, 16, 1)
        >>> print(cnf.input_channels)
    """

    def __init__(
            self,
            expand_ratio: float,
            kernel_size: int,
            stride: int,
            in_chs: int,
            out_chs: int,
            num_layers: int,
            width_cnf: float,
            depth_cnf: float,
    ) -> None:
        self.expand_ratio = expand_ratio
        self.kernel_size = kernel_size
        self.stride = stride
        self.input_channels = self.adjust_channels(in_chs, width_cnf)
        self.out_channels = self.adjust_channels(out_chs, width_cnf)
        self.num_layers = self.adjust_depth(num_layers, depth_cnf)

    @staticmethod
    def adjust_channels(channels: int, width_cnf: float, min_value: Optional[int] = None) -> int:
        """Calculate the width of MBConv."""
        return make_divisible(channels * width_cnf, 8, min_value)

    @staticmethod
    def adjust_depth(num_layers: int, depth_cnf: float) -> int:
        """Calculate the depth of MBConv."""
        return int(math.ceil(num_layers * depth_cnf))


class MBConv(nn.Cell):
    """
    MBConv Module.

    Args:
        cnf (MBConvConfig): The class which contains the parameters(in_channels, out_channels, nums_layers) and
        the functions which help calculate the parameters after multipling the expand_ratio.
        keep_prob: The dropout rate in MBConv.
        norm (nn.Cell): The BatchNorm Method.Default: None.
        se_layer (nn.Cell): The squeeze-excite Module. Default: SqueezeExcite.

    Returns:
        Tensor

    Example:
        >>> cnf = MBConvConfig(1, 3, 1, 32, 16, 1)
        >>> x = Tensor(np.ones(1, 2, 2, 2), mindspore.float32)
        >>> MBConv(cnf, 0.2, None)(x)
    """

    def __init__(
            self,
            cnf: MBConvConfig,
            keep_prob: float,
            norm: Optional[nn.Cell] = None,
            se_layer: Callable[..., nn.Cell] = SqueezeExcite,
    ) -> None:
        super().__init__()

        Validator.check_int_range(cnf.stride, 1, 2, Rel.INC_BOTH, "stride")

        self.shortcut = cnf.stride == 1 and cnf.input_channels == cnf.out_channels

        layers: List[nn.Cell] = []
        activation = Swish

        # expand conv: the out_channels is cnf.expand_ratio times of the in_channels.
        expanded_channels = cnf.adjust_channels(cnf.input_channels, cnf.expand_ratio)
        if expanded_channels != cnf.input_channels:
            layers.append(
                ConvNormActivation(
                    cnf.input_channels,
                    expanded_channels,
                    kernel_size=1,
                    norm=norm,
                    activation=activation,
                )
            )

        # depthwise conv: splits the filter into groups.
        layers.append(
            ConvNormActivation(
                expanded_channels,
                expanded_channels,
                kernel_size=cnf.kernel_size,
                stride=cnf.stride,
                groups=expanded_channels,
                norm=norm,
                activation=activation,
            )
        )

        # squeeze and excitation
        squeeze_channels = max(1, cnf.input_channels // 4)
        layers.append(se_layer(expanded_channels, squeeze_channels, Swish, "sigmoid"))

        # project
        layers.append(
            ConvNormActivation(
                expanded_channels, cnf.out_channels, kernel_size=1, norm=norm, activation=None
            )
        )

        self.block = nn.SequentialCell(layers)
        self.dropout = DropConnect(keep_prob)
        self.out_channels = cnf.out_channels

    def construct(self, x) -> Tensor:
        """MBConv construct."""
        result = self.block(x)
        if self.shortcut:
            result = self.dropout(result)
            result += x
        return result


@ClassFactory.register(ModuleType.BACKBONE)
class EfficientNet(nn.Cell):
    """
    EfficientNet architecture.

    Args:
        inverted_residual_setting (List[MBConvConfig]): The settings of block.
        width_mult (float): The ratio of the channel. Default: 1.0.
        depth_mult (float): The ratio of num_layers. Default: 1.0.
        keep_prob (float): The dropout rate of MBConv. Default: 0.2.
        block (Optional[Callable[..., nn.Cell]]): The basic block of the model. Default: None.
        norm_layer (Optional[Callable[..., nn.Cell]]): The normalization layer. Default: None.

    Returns:
        Tensor

    Examples:
        >>> inverted_residual_setting = [MBConvConfig(1, 3, 1, 32, 16, 1)]
        >>> EfficientNet(inverted_residual_setting, 0.2)
    """

    def __init__(
            self,
            width_mult: float,
            depth_mult: float,
            inverted_residual_setting: Optional[List[MBConvConfig]] = None,
            keep_prob: float = 0.2,
            block: Optional[nn.Cell] = None,
            norm_layer: Optional[nn.Cell] = None,
    ) -> None:
        super(EfficientNet, self).__init__()

        if block is None:
            block = MBConv

        if norm_layer is None:
            if width_mult >= 1.6:
                norm_layer = partial(nn.BatchNorm2d, eps=0.001, momentum=0.99)
            norm_layer = nn.BatchNorm2d

        layers: List[nn.Cell] = []

        bneck_conf = partial(MBConvConfig, width_cnf=width_mult, depth_cnf=depth_mult)

        if not inverted_residual_setting:
            inverted_residual_setting = [
                bneck_conf(1, 3, 1, 32, 16, 1),
                bneck_conf(6, 3, 2, 16, 24, 2),
                bneck_conf(6, 5, 2, 24, 40, 2),
                bneck_conf(6, 3, 2, 40, 80, 3),
                bneck_conf(6, 5, 1, 80, 112, 3),
                bneck_conf(6, 5, 2, 112, 192, 4),
                bneck_conf(6, 3, 1, 192, 320, 1),
            ]

        # building first layer
        firstconv_output_channels = inverted_residual_setting[0].input_channels
        layers.append(
            ConvNormActivation(
                3, firstconv_output_channels, kernel_size=3, stride=2, norm=norm_layer, activation=Swish
            )
        )

        # building MBConv blocks
        total_stage_blocks = sum(cnf.num_layers for cnf in inverted_residual_setting)
        stage_block_id = 0

        # cnf is the settings of block
        for cnf in inverted_residual_setting:
            stage: List[nn.Cell] = []

            # cnf.num_layers is the num of the same block
            for _ in range(cnf.num_layers):
                # copy to avoid modifications. shallow copy is enough
                block_cnf = copy.copy(cnf)

                # overwrite info if not the first conv in the stage
                if stage:
                    block_cnf.input_channels = block_cnf.out_channels
                    block_cnf.stride = 1

                # adjust dropout rate of blocks based on the depth of the stage block
                sd_prob = keep_prob * float(stage_block_id) / total_stage_blocks

                stage.append(block(block_cnf, sd_prob, norm_layer))
                stage_block_id += 1

            layers.append(nn.SequentialCell(stage))

        # building last several layers
        lastconv_input_channels = inverted_residual_setting[-1].out_channels
        lastconv_output_channels = 4 * lastconv_input_channels
        layers.append(
            ConvNormActivation(
                lastconv_input_channels,
                lastconv_output_channels,
                kernel_size=1,
                norm=norm_layer,
                activation=Swish,
            )
        )

        self.features = nn.SequentialCell(layers)
        self.avgpool = P.AdaptiveAvgPool2D(1)

    def construct(self, x) -> Tensor:
        """Efficientnet construct."""
        x = self.features(x)

        x = self.avgpool(x)
        x = P.Flatten()(x)

        return x
