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
""" Darknet backbone """

from mindspore import nn
from mindspore.ops import operations as P

from mindvision.engine.class_factory import ClassFactory, ModuleType
from mindvision.engine.utils.config import Config


def conv_block(in_channels,
               out_channels,
               kernel_size,
               stride,
               action_func,
               momentum=0.9,
               dilation=1):
    """Get a conv2d batch_norm with action function layer"""
    pad_mode = 'same'
    padding = 0

    return nn.SequentialCell(
        [nn.Conv2d(in_channels,
                   out_channels,
                   kernel_size=kernel_size,
                   stride=stride,
                   padding=padding,
                   dilation=dilation,
                   pad_mode=pad_mode),
         nn.BatchNorm2d(out_channels, momentum=momentum),
         action_func]
    )


class ResidualBlock(nn.Cell):
    """
    DarkNet V1 residual block definition.

    Args:
        in_channels: Integer. Input channel.
        out_channels: Integer. Output channel.

    Returns:
        Tensor, output tensor.
    Examples:
        ResidualBlock(3, 208, nn.Relu, 0.9)
    """

    def __init__(self,
                 in_channels,
                 out_channels,
                 action_func,
                 momentum):
        super(ResidualBlock, self).__init__()
        out_chs = out_channels // 2
        self.conv1 = conv_block(in_channels, out_chs, kernel_size=1, stride=1,
                                action_func=action_func, momentum=momentum)
        self.conv2 = conv_block(out_chs, out_channels, kernel_size=3, stride=1,
                                action_func=action_func, momentum=momentum)
        self.add = P.Add()

    def construct(self, x):
        """ build netword """
        identity = x
        out = self.conv1(x)
        out = self.conv2(out)
        out = self.add(out, identity)

        return out


class CspResidualBlock(ResidualBlock):
    """
    DarkNet V1 residual block definition.

    Args:
        in_channels: Integer. Input channel.
        out_channels: Integer. Output channel.

    Returns:
        Tensor, output tensor.
    Examples:
        ResidualBlock(3, 208, nn.Relu, 0.9)
    """

    def __init__(self,
                 in_channels,
                 out_channels,
                 action_func,
                 momentum):
        super(CspResidualBlock, self).__init__(in_channels, out_channels,
                                               action_func, momentum)
        out_chs = out_channels
        self.conv1 = conv_block(in_channels, out_chs, kernel_size=1, stride=1,
                                action_func=action_func, momentum=momentum)
        self.conv2 = conv_block(out_chs, out_channels, kernel_size=3, stride=1,
                                action_func=action_func, momentum=momentum)


class CspStep(nn.Cell):
    """
        CspDarkNet V1 layer generator.

        Args:
            in_channels: Integer. Input channel.
            out_channels: Integer. Output channel.
            action_func:
            layers:
            momentum:

        Returns:
            Tensor, output tensor.
        Examples:
            CspStep(3, 208, nn.Relu, layers, 0.9)
    """

    def __init__(self,
                 in_channels,
                 out_channels,
                 action_func,
                 layers,
                 momentum=0.9):
        super(CspStep, self).__init__()

        self.action_func = action_func
        self.layers = layers
        out_chs = out_channels // 2

        self.trans0 = conv_block(in_channels, out_chs, kernel_size=1, stride=1,
                                 action_func=action_func, momentum=momentum)
        self.trans1 = conv_block(in_channels, out_chs, kernel_size=1, stride=1,
                                 action_func=action_func, momentum=momentum)

        self.conv1 = conv_block(out_chs, out_chs, kernel_size=1, stride=1,
                                action_func=action_func, momentum=momentum)
        self.conv2 = conv_block(out_channels, out_channels, kernel_size=1,
                                stride=1,
                                action_func=action_func,
                                momentum=momentum)

        self.concat = P.Concat(axis=1)

    def construct(self, x):
        """ build netword """
        tran0 = self.trans0(x)
        tran1 = self.trans1(x)
        residual = self.layers(tran0)
        c1 = self.conv1(residual)
        concat_block = self.concat((c1, tran1))
        c2 = self.conv2(concat_block)
        return c2


class CspFirstLayer(nn.Cell):
    """ CspDarknet First layer """

    def __init__(self,
                 in_channels,
                 out_channels,
                 action_func,
                 momentum=0.9):
        super(CspFirstLayer, self).__init__()

        out_chs = out_channels // 2
        in_chs = out_channels * 2
        self.trans0 = conv_block(in_channels, out_channels, kernel_size=1,
                                 stride=1,
                                 action_func=action_func, momentum=momentum)
        self.trans1 = conv_block(in_channels, out_channels, kernel_size=1,
                                 stride=1,
                                 action_func=action_func, momentum=momentum)

        self.conv1 = conv_block(out_channels, out_chs, kernel_size=1, stride=1,
                                action_func=action_func, momentum=momentum)
        self.conv2 = conv_block(out_chs, out_channels, kernel_size=3,
                                stride=1,
                                action_func=action_func,
                                momentum=momentum)
        self.conv3 = conv_block(out_channels, out_channels, kernel_size=1,
                                stride=1,
                                action_func=action_func,
                                momentum=momentum)
        self.conv4 = conv_block(in_chs, out_channels, kernel_size=1,
                                stride=1,
                                action_func=action_func,
                                momentum=momentum)

        self.add = P.Add()
        self.concat = P.Concat(axis=1)

    def construct(self, x):
        """ build netword """
        tran0 = self.trans0(x)
        c1 = self.conv1(tran0)
        c2 = self.conv2(c1)
        c3 = self.add(tran0, c2)
        c4 = self.conv3(c3)
        tran1 = self.trans1(x)
        concat = self.concat((c4, tran1))
        c5 = self.conv4(concat)
        return c5


class Mish(nn.Cell):
    """Mish activation method"""

    def __init__(self):
        super(Mish, self).__init__()
        self.mul = P.Mul()
        self.tanh = P.Tanh()
        self.softplus = P.Softplus()

    def construct(self, input_x):
        """ build netword """
        res1 = self.softplus(input_x)
        tanh = self.tanh(res1)
        output = self.mul(input_x, tanh)

        return output


class DarkNetV1(nn.Cell):
    """
    Base DarkNet V1 network.

    Args:
        config: Config dictionary.
        action_func: activate function
        momentum: momentum
        detect: Bool. Whether detect or not. Default:False.

    Returns:
        Tuple, tuple of output tensor,(f3,f4,f5).

    """

    def __init__(self,
                 config,
                 block,
                 action_func,
                 momentum=0.1,
                 detect=False):
        super(DarkNetV1, self).__init__()

        self.block = block
        self.layer_nums = config.layer_nums
        self.in_channels = config.in_channels
        self.out_channels = config.out_channels
        self.action_func = action_func
        self.out_channel = config.out_channels[-1]
        self.detect = detect
        self.momentum = momentum

        self.conv0 = conv_block(3, self.in_channels[0], kernel_size=3,
                                stride=1, action_func=action_func,
                                momentum=momentum)
        self.conv1 = conv_block(self.in_channels[0], self.out_channels[0],
                                kernel_size=3, stride=2,
                                action_func=action_func,
                                momentum=momentum)
        self.conv2 = conv_block(self.in_channels[1], self.out_channels[1],
                                kernel_size=3,
                                stride=2,
                                action_func=action_func,
                                momentum=momentum)
        self.conv3 = conv_block(self.in_channels[2], self.out_channels[2],
                                kernel_size=3,
                                stride=2, action_func=action_func,
                                momentum=momentum)
        self.conv4 = conv_block(self.in_channels[3], self.out_channels[3],
                                kernel_size=3,
                                stride=2, action_func=action_func,
                                momentum=momentum)
        self.conv5 = conv_block(self.in_channels[4], self.out_channels[4],
                                kernel_size=3,
                                stride=2, action_func=action_func,
                                momentum=momentum)
        self.layer1 = self.make_layer(self.block, self.layer_nums[0],
                                      self.out_channels[0],
                                      self.out_channels[0], self.action_func)
        self.layer2 = self.make_layer(self.block, self.layer_nums[1],
                                      self.out_channels[1],
                                      self.out_channels[1], self.action_func)
        self.layer3 = self.make_layer(self.block, self.layer_nums[2],
                                      self.out_channels[2],
                                      self.out_channels[2], self.action_func)
        self.layer4 = self.make_layer(self.block,
                                      self.layer_nums[3],
                                      self.out_channels[3],
                                      self.out_channels[3],
                                      self.action_func)
        self.layer5 = self.make_layer(self.block, self.layer_nums[4],
                                      self.out_channels[4],
                                      self.out_channels[4],
                                      self.action_func)

    def make_layer(self, block, layer_num,
                   in_channel, out_channel, action_func):
        """
            Make Layer for DarkNet.

            :param block: Cell. DarkNet block.
            :param layer_num: Integer. Layer number.
            :param in_channel: Integer. Input channel.
            :param out_channel: Integer. Output channel.
            :param action_func: action function.

            Examples:
                make_layer(ConvBlock, 1, 128, 256, nn.Relu)
        """
        layers = []
        dark_blk = block(in_channel, out_channel, action_func, self.momentum)
        layers.append(dark_blk)

        for _ in range(1, layer_num):
            dark_blk = block(out_channel, out_channel,
                             action_func, self.momentum)
            layers.append(dark_blk)

        return nn.SequentialCell(layers)

    def construct(self, x):
        """ build netword """
        c1 = self.conv0(x)
        c2 = self.conv1(c1)
        c3 = self.layer1(c2)
        c4 = self.conv2(c3)
        c5 = self.layer2(c4)
        c6 = self.conv3(c5)
        c7 = self.layer3(c6)
        c8 = self.conv4(c7)
        c9 = self.layer4(c8)
        c10 = self.conv5(c9)
        c11 = self.layer5(c10)
        if self.detect:
            return c7, c9, c11

        return c11

    def get_out_channels(self):
        """ get the output channels """
        return self.out_channel


@ClassFactory.register(ModuleType.BACKBONE)
class DarkNet(DarkNetV1):
    """
    DarkNet V1 network.

    Args:
        block: Cell. Block for network.
        layer_nums: List. Numbers of different layers.
        in_channels: Integer. Input channel.
        out_channels: Integer. Output channel.
        detect: Bool. Whether detect or not. Default:False.

    Returns:
        Tuple, tuple of output tensor,(f1,f2,f3,f4,f5).

    Examples:
        DarkNet(ResidualBlock,
               [1, 2, 8, 8, 4],
               [32, 64, 128, 256, 512],
               [64, 128, 256, 512, 1024],
               False)
    """

    def __init__(self, **kwargs):
        super(DarkNet, self).__init__(Config(**kwargs),
                                      ResidualBlock,
                                      nn.ReLU(),
                                      detect=True)


@ClassFactory.register(ModuleType.BACKBONE)
class CspDarkNet(DarkNetV1):
    """
    DarkNet V1 network with CSP.

    Args:
        config: CspDarkNet Config dictionary.

    Returns:
        Tuple, tuple of output tensor,(f3,f4,f5).

    Examples:
        DarkNet(**kwargs)
    """

    def __init__(self, **kwargs):
        super(CspDarkNet, self).__init__(Config(**kwargs),
                                         CspResidualBlock,
                                         Mish(),
                                         detect=True)
        self.config = Config(**kwargs)
        self.layer1 = CspFirstLayer(self.config.out_channels[0],
                                    self.config.out_channels[0], Mish())

    def make_layer(self, block, layer_num,
                   in_channel, out_channel, action_func):
        """
        Make Layer for DarkNet.

        Args:
            block: Cell. DarkNet block.
            layer_num: Integer. Layer number.
            in_channel: Integer. Input channel.
            out_channel: Integer. Output channel.
            action_func: action function.
            SequentialCell, the output layer.

        Examples:
            make_layer(ConvBlock, 1, 128, 256, Mish())
        """
        layers = super(CspDarkNet, self) \
            .make_layer(block, layer_num,
                        in_channel // 2, out_channel // 2,
                        action_func)
        csp_layer = CspStep(in_channel,
                            out_channel,
                            action_func,
                            layers)
        return csp_layer
