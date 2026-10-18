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
"""Resnet backbone."""

from typing import Type, Union, List, Optional

from mindspore import nn

from mindvision.classification.models.blocks import ConvNormActivation
from mindvision.engine.class_factory import ClassFactory, ModuleType

__all__ = [
    'ResidualBlockBase',
    'ResidualBlock',
    'ResNet',
    'ResNet18',  # registration mechanism to use yaml configuration
    'ResNet34',  # registration mechanism to use yaml configuration
    'ResNet50',  # registration mechanism to use yaml configuration
    'ResNet101',  # registration mechanism to use yaml configuration
    'ResNet152'  # registration mechanism to use yaml configuration
]


class ResidualBlockBase(nn.Cell):
    """
    ResNet residual block base definition.

    Args:
        in_channel (int): Input channel.
        out_channel (int): Output channel.
        stride (int): Stride size for the first convolutional layer. Default: 1.
        group (int): Group convolutions. Default: 1.
        base_with (int): Width of per group. Default: 64.
        norm (nn.Cell, optional): Module specifying the normalization layer to use. Default: None.
        down_sample (nn.Cell, optional): Downsample structure. Default: None.

    Returns:
        Tensor, output tensor.

    Examples:
        >>> ResidualBlockBase(3, 256, stride=2)
    """

    expansion: int = 1

    def __init__(self,
                 in_channel: int,
                 out_channel: int,
                 stride: int = 1,
                 group: int = 1,
                 base_width: int = 64,
                 norm: Optional[nn.Cell] = None,
                 down_sample: Optional[nn.Cell] = None
                 ) -> None:
        super(ResidualBlockBase, self).__init__()
        if not norm:
            norm = nn.BatchNorm2d
        assert group != 1 or base_width == 64, "ResidualBlockBase only supports groups=1 and base_width=64"
        self.conv1 = ConvNormActivation(
            in_channel,
            out_channel,
            kernel_size=3,
            stride=stride,
            norm=norm)
        self.conv2 = ConvNormActivation(
            out_channel,
            out_channel,
            kernel_size=3,
            norm=norm,
            activation=None)
        self.relu = nn.ReLU()
        self.down_sample = down_sample

    def construct(self, x):
        """ResidualBlockBase construct."""
        identity = x

        out = self.conv1(x)
        out = self.conv2(out)

        if self.down_sample:
            identity = self.down_sample(x)
        out += identity
        out = self.relu(out)

        return out


class ResidualBlock(nn.Cell):
    """
    ResNet residual block definition.

    Args:
        in_channel (int): Input channel.
        out_channel (int): Output channel.
        stride (int): Stride size for the second convolutional layer. Default: 1.
        group (int): Group convolutions. Default: 1.
        base_with (int): Width of per group. Default: 64.
        norm (nn.Cell, optional): Module specifying the normalization layer to use. Default: None.
        down_sample (nn.Cell, optional): Downsample structure. Default: None.

    Returns:
        Tensor, output tensor.

    Examples:
        >>> ResidualBlock(3, 256, stride=2)
    """

    expansion: int = 4

    def __init__(self,
                 in_channel: int,
                 out_channel: int,
                 stride: int = 1,
                 group: int = 1,
                 base_width: int = 64,
                 norm: Optional[nn.Cell] = None,
                 down_sample: Optional[nn.Cell] = None
                 ) -> None:
        super(ResidualBlock, self).__init__()
        if not norm:
            norm = nn.BatchNorm2d
        out_channel = int(out_channel * (base_width / 64.0)) * group

        self.conv1 = ConvNormActivation(
            in_channel, out_channel, kernel_size=1, norm=norm)
        self.conv2 = ConvNormActivation(
            out_channel,
            out_channel,
            kernel_size=3,
            stride=stride,
            groups=group,
            norm=norm)
        self.conv3 = ConvNormActivation(
            out_channel,
            out_channel *
            self.expansion,
            kernel_size=1,
            norm=norm,
            activation=None)
        self.relu = nn.ReLU()
        self.down_sample = down_sample

    def construct(self, x):
        """ResidualBlock construct."""
        identity = x

        out = self.conv1(x)
        out = self.conv2(out)
        out = self.conv3(out)

        if self.down_sample:
            identity = self.down_sample(x)

        out += identity
        out = self.relu(out)

        return out


class ResNet(nn.Cell):
    """
    ResNet architecture.

    Args:
        block (Type[Union[ResidualBlockBase, ResidualBlock]]): Block for network.
        layer_nums (List[int]): Numbers of block in different layers.
        group (int): Group convolutions. Default: 1.
        base_width (int): Width of per group. Default: 64.
        norm (nn.Cell, optional): Module specifying the normalization layer to use. Default: None.

    Returns:
        Tensor, output tensor.

    Examples:
        >>> ResNet(ResidualBlock, [3, 4, 6, 3])
    """

    def __init__(self,
                 block: Type[Union[ResidualBlockBase, ResidualBlock]],
                 layer_nums: List[int],
                 group: int = 1,
                 base_with: int = 64,
                 norm: Optional[nn.Cell] = None
                 ) -> None:
        super(ResNet, self).__init__()
        if not norm:
            norm = nn.BatchNorm2d
        self.norm = norm
        self.in_channels = 64
        self.group = group
        self.base_with = base_with
        self.conv1 = ConvNormActivation(
            3, self.in_channels, kernel_size=7, stride=2, norm=norm)
        self.max_pool = nn.MaxPool2d(kernel_size=3, stride=2, pad_mode='same')
        self.layer1 = self._make_layer(block, 64, layer_nums[0])
        self.layer2 = self._make_layer(block, 128, layer_nums[1], stride=2)
        self.layer3 = self._make_layer(block, 256, layer_nums[2], stride=2)
        self.layer4 = self._make_layer(block, 512, layer_nums[3], stride=2)

    def _make_layer(self,
                    block: Type[Union[ResidualBlockBase, ResidualBlock]],
                    channel: int,
                    block_nums: int,
                    stride: int = 1
                    ):
        """Block layers."""
        down_sample = None

        if stride != 1 or self.in_channels != self.in_channels * block.expansion:
            down_sample = ConvNormActivation(
                self.in_channels,
                channel * block.expansion,
                kernel_size=1,
                stride=stride,
                norm=self.norm,
                activation=None)
        layers = []
        layers.append(
            block(
                self.in_channels,
                channel,
                stride=stride,
                down_sample=down_sample,
                group=self.group,
                base_width=self.base_with,
                norm=self.norm
            )
        )
        self.in_channels = channel * block.expansion

        for _ in range(1, block_nums):
            layers.append(
                block(
                    self.in_channels,
                    channel,
                    group=self.group,
                    base_width=self.base_with,
                    norm=self.norm
                )
            )

        return nn.SequentialCell(layers)

    def construct(self, x):
        x = self.conv1(x)
        x = self.max_pool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        return x


@ClassFactory.register(ModuleType.BACKBONE)
class ResNet18(ResNet):
    """
    The class of ResNet18 uses the registration mechanism to register, need to use the yaml configuration file to call.
    """

    def __init__(self, **kwargs):
        super(
            ResNet18, self).__init__(ResidualBlockBase, [2, 2, 2, 2], **kwargs)


@ClassFactory.register(ModuleType.BACKBONE)
class ResNet34(ResNet):
    """
    The class of ResNet34 uses the registration mechanism to register, need to use the yaml configuration file to call.
    """

    def __init__(self, **kwargs):
        super(
            ResNet34, self).__init__(ResidualBlockBase, [3, 4, 6, 3], **kwargs)


@ClassFactory.register(ModuleType.BACKBONE)
class ResNet50(ResNet):
    """
    The class of ResNet50 uses the registration mechanism to register, need to use the yaml configuration file to call.
    """

    def __init__(self, **kwargs):
        super(ResNet50, self).__init__(ResidualBlock, [3, 4, 6, 3], **kwargs)


@ClassFactory.register(ModuleType.BACKBONE)
class ResNet101(ResNet):
    """
    The class of ResNet101 uses the registration mechanism to register, need to use the yaml configuration file to call.
    """

    def __init__(self, **kwargs):
        super(ResNet101, self).__init__(ResidualBlock, [3, 4, 23, 3], **kwargs)


@ClassFactory.register(ModuleType.BACKBONE)
class ResNet152(ResNet):
    """
    The class of ResNet152 uses the registration mechanism to register, need to use the yaml configuration file to call.
    """

    def __init__(self, **kwargs):
        super(ResNet152, self).__init__(ResidualBlock, [3, 8, 36, 3], **kwargs)
