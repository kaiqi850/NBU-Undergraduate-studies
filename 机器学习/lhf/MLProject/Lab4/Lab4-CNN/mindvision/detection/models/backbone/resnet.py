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
"""ResNet Full X."""

import mindspore.nn as nn
from mindspore.ops import functional as F
from mindspore.ops import operations as P
from mindvision.detection.models.utils.custom_op import (SEBlock, GroupConv, custom_conv,
                                                         custom_bn, custom_down_sample)

from mindvision.engine.class_factory import ClassFactory, ModuleType


class ResidualBlock(nn.Cell):
    """ResNet V2 residual block definition.

    Args:
        in_channel (int): Input channel.
        out_channel (int): Output channel.
        stride (int): Stride size for the first convolutional layer. Default: 1.
        use_se (bool): Enable SE-ResNet50 net. Default: False.

    Returns:
        Tensor, output tensor.

    Examples:
        >>> ResidualBlock(3, 256, stride=2)
    """
    expansion = 4

    def __init__(self,
                 in_channel,
                 out_channel,
                 stride=1,
                 depth=50,
                 momentum=0.1,
                 norm_layer='BN2d',
                 activation="relu",
                 pad_mode='pad',
                 base_width=64,
                 groups=1,
                 weights_update=False,
                 bn_training=False,
                 down_sample=False,
                 use_se=False,
                 use_group=False,
                 default_bn=False):
        super(ResidualBlock, self).__init__()

        self.stride = stride
        self.affine = weights_update
        self.down_sample = down_sample
        self.use_se = use_se
        self.use_group = use_group

        channel = int(out_channel * (base_width / 64.0) * groups // self.expansion)

        self.conv1 = custom_conv(in_channel, channel, kernel_size=1, stride=1, padding=0,
                                 activation=activation, depth=depth)
        self.bn1 = custom_bn(channel, norm_layer=norm_layer, momentum=momentum,
                             affine=self.affine, use_batch_statistics=bn_training, default_bn=default_bn)

        self.conv2 = custom_conv(channel, channel, kernel_size=3, stride=stride, padding=1,
                                 activation=activation, depth=depth)
        self.bn2 = custom_bn(channel, norm_layer=norm_layer, momentum=momentum,
                             affine=self.affine, use_batch_statistics=bn_training, default_bn=default_bn)

        self.conv3 = custom_conv(channel, out_channel, kernel_size=1, stride=1, padding=0,
                                 activation=activation, depth=depth)
        self.bn3 = custom_bn(out_channel, norm_layer=norm_layer, momentum=momentum,
                             affine=self.affine, use_batch_statistics=bn_training, default_bn=default_bn)

        if self.use_group:
            self.conv2 = GroupConv(channel, channel, 3, stride, pad=1, groups=groups)

        if bn_training:
            self.bn1 = self.bn1.set_train()
            self.bn2 = self.bn2.set_train()
            self.bn3 = self.bn3.set_train()

        if not weights_update:
            self.conv1.weight.requires_grad = False
            if not self.use_group:
                self.conv2.weight.requires_grad = False
            self.conv3.weight.requires_grad = False

        self.relu = P.ReLU()

        if self.use_se:
            self.se = SEBlock(out_channel)

        self.down_sample_layer = None
        if self.down_sample:
            self.down_sample_layer = custom_down_sample(
                in_channel, out_channel, stride, momentum=momentum,
                affine=self.affine, use_batch_statistics=bn_training,
                norm_layer=norm_layer, pad_mode=pad_mode,
                activation=activation, depth=depth, default_bn=default_bn
            )

        self.add = P.Add()

    def construct(self, x):
        """Residual block construct."""
        identity = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.use_se:
            out = self.se(out)

        if self.down_sample:
            identity = self.down_sample_layer(identity)

        out = self.add(out, identity)
        out = self.relu(out)

        return out


class ResidualBlockBase(nn.Cell):
    """
    ResNet V2 residual block definition.

    Args:
        in_channel (int): Input channel.
        out_channel (int): Output channel.
        stride (int): Stride size for the first convolutional layer. Default: 1.

    Returns:
        Tensor, output tensor.

    Examples:
        >>> ResidualBlockBase(3, 256, stride=2)
    """

    def __init__(self,
                 in_channel,
                 out_channel,
                 stride=1,
                 depth=50,
                 momentum=0.1,
                 norm_layer='BN2d',
                 activation="relu",
                 pad_mode='pad',
                 weights_update=False,
                 bn_training=False,
                 down_sample=False,
                 use_se=False,
                 default_bn=False):
        super(ResidualBlockBase, self).__init__()

        self.affine = weights_update
        self.use_se = use_se
        self.down_sample = down_sample

        self.conv1 = custom_conv(in_channel, out_channel, kernel_size=3, stride=stride, padding=1,
                                 activation=activation, depth=depth)
        self.bn1d = custom_bn(out_channel, norm_layer=norm_layer, momentum=momentum,
                              affine=self.affine, use_batch_statistics=bn_training,
                              default_bn=default_bn)

        self.conv2 = custom_conv(out_channel, out_channel, kernel_size=3, stride=1, padding=1,
                                 activation=activation, depth=depth)
        self.bn2d = custom_bn(out_channel, norm_layer=norm_layer, momentum=momentum,
                              affine=self.affine, use_batch_statistics=bn_training,
                              default_bn=default_bn)

        self.relu = nn.ReLU()

        if bn_training:
            self.bn1d = self.bn1d.set_train()
            self.bn2d = self.bn2d.set_train()

        if not weights_update:
            self.conv1.weight.requires_grad = False
            self.conv2.weight.requires_grad = False

        if self.use_se:
            self.se = SEBlock(out_channel)

        self.down_sample_layer = None
        if self.down_sample:
            self.down_sample_layer = custom_down_sample(
                in_channel, out_channel, stride, momentum=momentum,
                affine=self.affine, use_batch_statistics=bn_training,
                norm_layer=norm_layer, pad_mode=pad_mode,
                activation=activation, depth=depth, default_bn=default_bn
            )

        self.add = P.Add()

    def construct(self, x):
        """Base residual block construct."""
        identity = x

        out = self.conv1(x)
        out = self.bn1d(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2d(out)

        if self.use_se:
            out = self.se(out)

        if self.down_sample:
            identity = self.down_sample_layer(identity)

        out = self.add(out, identity)
        out = self.relu(out)

        return out


@ClassFactory.register(ModuleType.BACKBONE)
class ResNet(nn.Cell):
    """
    ResNetPlus architecture.

    Args:
        depth (int): ResNet depth.
        strides (list):  Stride size in each layer.
        use_se (bool): Enable SE-ResNet50 net. Default: False.

    Returns:
        Tensor, output tensor.

    Examples:
        >>> ResNet(50, [1, 2, 2, 2], 10)
    """

    network_arch = {
        18: (ResidualBlockBase,
             (2, 2, 2, 2)),
        34: (ResidualBlockBase,
             (3, 4, 6, 3)),
        50: (ResidualBlock,
             (3, 4, 6, 3)),
        101: (ResidualBlock,
              (3, 4, 23, 3)),
        152: (ResidualBlock,
              (3, 8, 36, 3))
    }

    def __init__(self,
                 depth,
                 strides,
                 in_channels,
                 out_channels,
                 momentum=0.1,
                 width_per_group=64,
                 groups=1,
                 norm_layer='BN2d',
                 activation="relu",
                 bn_training=False,
                 weights_update=True,
                 default_bn=False,
                 use_se=False,
                 use_group=False):
        super(ResNet, self).__init__()

        if not isinstance(depth, int):
            raise ValueError(
                "The network depth should be int type, but get {} type.".format(type(depth)))

        network_params = self.network_arch.get(depth)
        block, layer_nums = network_params

        if not len(layer_nums) == len(in_channels) == len(out_channels) == 4:
            raise ValueError("The length of network's layer numbers, input channels, output channels list must be 4!")

        self.base_width = width_per_group
        self.groups = groups
        self.activation = activation
        self.weights_update = weights_update
        self.bn_training = bn_training
        self.depth = depth
        self.use_se = use_se
        self.use_group = use_group

        self.conv1 = custom_conv(3, 64, kernel_size=7, stride=2, padding=3,
                                 activation=self.activation, depth=self.depth)

        self.bn1 = custom_bn(64, norm_layer=norm_layer, momentum=momentum,
                             affine=self.bn_training, use_batch_statistics=self.bn_training,
                             default_bn=default_bn)
        self.relu = P.ReLU()

        self.max_pool = P.MaxPool(kernel_size=3, strides=2, pad_mode="SAME")

        if not self.weights_update:
            self.conv1.weight.requires_grad = False

        self.layer1 = self._make_layer(block,
                                       layer_nums[0],
                                       in_channel=in_channels[0],
                                       out_channel=out_channels[0],
                                       stride=strides[0],
                                       momentum=momentum,
                                       weights_update=self.weights_update,
                                       default_bn=default_bn)
        self.layer2 = self._make_layer(block,
                                       layer_nums[1],
                                       in_channel=in_channels[1],
                                       out_channel=out_channels[1],
                                       stride=strides[1],
                                       momentum=momentum,
                                       weights_update=True,
                                       default_bn=default_bn)
        self.layer3 = self._make_layer(block,
                                       layer_nums[2],
                                       in_channel=in_channels[2],
                                       out_channel=out_channels[2],
                                       stride=strides[2],
                                       momentum=momentum,
                                       weights_update=True,
                                       default_bn=default_bn)
        self.layer4 = self._make_layer(block,
                                       layer_nums[3],
                                       in_channel=in_channels[3],
                                       out_channel=out_channels[3],
                                       stride=strides[3],
                                       momentum=momentum,
                                       weights_update=True,
                                       default_bn=default_bn)

    def _make_layer(self, block, layer_num, in_channel,
                    out_channel, stride, momentum, weights_update=False, default_bn=False):
        """
        Make stage network of ResNetPlus.

        Args:
            block (Cell): Resnet block.
            layer_num (int): Layer number.
            in_channel (int): Input channel.
            out_channel (int): Output channel.
            stride (int): Stride size for the first convolutional layer.
        Returns:
            SequentialCell, the output layer.

        Examples:
            >>> _make_layer(ResidualBlock, 3, 128, 256, 2)
        """
        layers = []

        down_sample = False
        if stride != 1 or in_channel != out_channel:
            down_sample = True

        resnet_block = block(in_channel, out_channel, stride=stride, depth=self.depth,
                             momentum=momentum, base_width=self.base_width, groups=self.groups,
                             weights_update=weights_update, bn_training=self.bn_training,
                             down_sample=down_sample, use_se=self.use_se, use_group=self.use_group,
                             default_bn=default_bn)
        layers.append(resnet_block)

        for _ in range(1, layer_num):
            resnet_block = block(out_channel, out_channel, stride=1, depth=self.depth,
                                 momentum=momentum, base_width=self.base_width, groups=self.groups,
                                 weights_update=weights_update, bn_training=self.bn_training,
                                 use_se=self.use_se, use_group=self.use_group,
                                 default_bn=default_bn)
            layers.append(resnet_block)

        return nn.SequentialCell(layers)

    def construct(self, x):
        """ResNetV2 construct."""
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)

        c1 = self.max_pool(x)

        c2 = self.layer1(c1)
        identity = c2

        if not self.weights_update:
            identity = F.stop_gradient(c2)

        c3 = self.layer2(identity)
        c4 = self.layer3(c3)
        c5 = self.layer4(c4)

        return identity, c3, c4, c5


def resnet18():
    """
    Get ResNet18 neural network.

    Returns:
        Cell, cell instance of ResNet18 neural network.

    Examples:
        >>> net = resnet18()
    """
    return ResNet(18, [1, 2, 2, 2],
                  [64, 256, 512, 1024],
                  [256, 512, 1024, 2048])


def resnet34():
    """
    Get ResNet34 neural network.

    Returns:
        Cell, cell instance of ResNet34 neural network.

    Examples:
        >>> net = resnet34()
    """
    return ResNet(34, [1, 2, 2, 2],
                  [64, 256, 512, 1024],
                  [256, 512, 1024, 2048])


def resnet50():
    """
    Get ResNet50 neural network.

    Returns:
        Cell, cell instance of ResNet50 neural network.

    Examples:
        >>> net = resnet50()
    """
    return ResNet(50, [1, 2, 2, 2],
                  [64, 256, 512, 1024],
                  [256, 512, 1024, 2048])


def se_resnet50():
    """
    Get SE_ResNet50 neural network.

    Returns:
        Cell, cell instance of ResNeXt50 neural network.

    Examples:
        >>> net = se_resnet50()
    """
    return ResNet(50, [1, 2, 2, 2],
                  [64, 256, 512, 1024],
                  [256, 512, 1024, 2048],
                  use_se=True)


def resnet101():
    """
    Get ResNet101 neural network.

    Returns:
        Cell, cell instance of ResNet101 neural network.

    Examples:
        >>> net = resnet101()
    """
    return ResNet(101, [1, 2, 2, 2],
                  [64, 256, 512, 1024],
                  [256, 512, 1024, 2048])


def resnet152():
    """
    Get ResNet152 neural network.

    Returns:
        Cell, cell instance of ResNet152 neural network.

    Examples:
        # >>> net = resnet152()
    """
    return ResNet(152, [1, 2, 2, 2],
                  [64, 256, 512, 1024],
                  [256, 512, 1024, 2048])


if __name__ == "__main__":
    resnet152 = resnet152()
    se_resnet50 = se_resnet50()
