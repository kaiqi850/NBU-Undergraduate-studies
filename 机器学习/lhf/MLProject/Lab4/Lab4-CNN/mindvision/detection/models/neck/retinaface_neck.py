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
""" Yolo neck implement"""
import math
from functools import reduce
import numpy as np

from mindspore import Tensor
from mindspore import nn
from mindspore.ops import operations as P

from mindvision.engine.class_factory import ClassFactory, ModuleType

def init_kaiming_uniform(arr_shape, a=0, nonlinearity='leaky_relu', has_bias=False):
    """Init_KaimingUniform"""
    def _calculate_in_and_out(arr_shape):
        dim = len(arr_shape)
        if dim < 2:
            raise ValueError("If initialize data with xavier uniform, the dimension of data must greater than 1.")

        n_in = arr_shape[1]
        n_out = arr_shape[0]

        if dim > 2:

            counter = reduce(lambda x, y: x * y, arr_shape[2:])
            n_in *= counter
            n_out *= counter
        return n_in, n_out

    def calculate_gain(nonlinearity, a=None):
        """relu"""
        linear_fans = ['linear', 'conv1d', 'conv2d', 'conv3d',
                       'conv_transpose1d', 'conv_transpose2d', 'conv_transpose3d']
        if nonlinearity in linear_fans or nonlinearity == 'sigmoid':
            return 1
        if nonlinearity == 'tanh':
            return 5.0 / 3
        if nonlinearity == 'relu':
            return math.sqrt(2.0)
        if nonlinearity == 'leaky_relu':
            if a is None:
                negative_slope = 0.01
            elif not isinstance(a, bool) and isinstance(a, int) or isinstance(a, float):
                negative_slope = a
            else:
                raise ValueError("negative_slope {} not a valid number".format(a))
            return math.sqrt(2.0 / (1 + negative_slope ** 2))

        raise ValueError("Unsupported nonlinearity {}".format(nonlinearity))

    fan_in, _ = _calculate_in_and_out(arr_shape)
    gain = calculate_gain(nonlinearity, a)
    std = gain / math.sqrt(fan_in)
    bound = math.sqrt(3.0) * std
    weight = np.random.uniform(-bound, bound, arr_shape).astype(np.float32)

    bias = None
    if has_bias:
        bound_bias = 1 / math.sqrt(fan_in)
        bias = np.random.uniform(-bound_bias, bound_bias, arr_shape[0:1]).astype(np.float32)
        bias = Tensor(bias)

    return Tensor(weight), bias


class ConvBNReLU(nn.SequentialCell):
    """ConvBNReLU wrapper."""
    def __init__(self, in_planes, out_planes, kernel_size, stride, padding, groups, norm_layer, leaky=0):
        weight_shape = (out_planes, in_planes, kernel_size, kernel_size)
        kaiming_weight, _ = init_kaiming_uniform(weight_shape, a=math.sqrt(5))

        super(ConvBNReLU, self).__init__(
            nn.Conv2d(in_planes, out_planes, kernel_size, stride, pad_mode='pad', padding=padding, group=groups,
                      has_bias=False, weight_init=kaiming_weight),
            norm_layer(out_planes),
            nn.LeakyReLU(alpha=leaky)
        )


class ConvBN(nn.SequentialCell):
    """ConvBN wrapper."""
    def __init__(self, in_planes, out_planes, kernel_size, stride, padding, groups, norm_layer):
        weight_shape = (out_planes, in_planes, kernel_size, kernel_size)
        kaiming_weight, _ = init_kaiming_uniform(weight_shape, a=math.sqrt(5))

        super(ConvBN, self).__init__(
            nn.Conv2d(in_planes, out_planes, kernel_size, stride, pad_mode='pad', padding=padding, group=groups,
                      has_bias=False, weight_init=kaiming_weight),
            norm_layer(out_planes),
        )


class RetinafaceFPN(nn.Cell):
    """FPN for Retinaface.

    Args:
        in_channels: Integer. Input channel.
        out_channels: Integer. Output channel.

    Returns:
        Tuple, tuple of output tensor,(f1,f2,f3).

    Examples:
        RetinafaceFPN(512, 1024, 2048)

    """
    def __init__(self, in_channels, out_channels):
        super(RetinafaceFPN, self).__init__()
        leaky = 0
        if out_channels <= 64:
            leaky = 0.1
        norm_layer = nn.BatchNorm2d
        self.output1 = ConvBNReLU(in_channels[0], out_channels, kernel_size=1, stride=1, padding=0, groups=1,
                                  norm_layer=norm_layer, leaky=leaky)
        self.output2 = ConvBNReLU(in_channels[1], out_channels, kernel_size=1, stride=1, padding=0, groups=1,
                                  norm_layer=norm_layer, leaky=leaky)
        self.output3 = ConvBNReLU(in_channels[2], out_channels, kernel_size=1, stride=1, padding=0, groups=1,
                                  norm_layer=norm_layer, leaky=leaky)

        self.merge1 = ConvBNReLU(out_channels, out_channels, kernel_size=3, stride=1, padding=1, groups=1,
                                 norm_layer=norm_layer, leaky=leaky)
        self.merge2 = ConvBNReLU(out_channels, out_channels, kernel_size=3, stride=1, padding=1, groups=1,
                                 norm_layer=norm_layer, leaky=leaky)

    def construct(self, inputs):
        """Construct of RetinafaceFPN."""
        output1 = self.output1(inputs[1])
        output2 = self.output2(inputs[2])
        output3 = self.output3(inputs[3])

        up3 = P.ResizeNearestNeighbor([P.Shape()(output2)[2], P.Shape()(output2)[3]])(output3)
        output2 = up3 + output2
        output2 = self.merge2(output2)

        up2 = P.ResizeNearestNeighbor([P.Shape()(output1)[2], P.Shape()(output1)[3]])(output2)
        output1 = up2 + output1
        output1 = self.merge1(output1)
        outs = (output1, output2, output3)
        return outs


class SSHBlock(nn.Cell):
    """SSHBlock for SSH.

    Args:
        in_channels: Integer. Input channel.
        out_channels: Integer. Output channel.

    Returns:
        Tensor, output tensor.

    Examples:
        SSHBlock(256, 256)

    """
    def __init__(self, in_channel, out_channel):
        super(SSHBlock, self).__init__()
        assert out_channel % 4 == 0
        leaky = 0
        if out_channel <= 64:
            leaky = 0.1
        norm_layer = nn.BatchNorm2d

        self.conv3x3 = ConvBN(in_channel, out_channel // 2, kernel_size=3, stride=1, padding=1, groups=1,
                              norm_layer=norm_layer)

        self.conv5x5_1 = ConvBNReLU(in_channel, out_channel // 4, kernel_size=3, stride=1, padding=1, groups=1,
                                    norm_layer=norm_layer, leaky=leaky)
        self.conv5x5_2 = ConvBN(out_channel // 4, out_channel // 4, kernel_size=3, stride=1, padding=1, groups=1,
                                norm_layer=norm_layer)

        self.conv7x7_2 = ConvBNReLU(out_channel // 4, out_channel // 4, kernel_size=3, stride=1, padding=1, groups=1,
                                    norm_layer=norm_layer, leaky=leaky)
        self.conv7x7_3 = ConvBN(out_channel // 4, out_channel // 4, kernel_size=3, stride=1, padding=1, groups=1,
                                norm_layer=norm_layer)

        self.cat = P.Concat(axis=1)
        self.relu = nn.ReLU()

    def construct(self, x):
        """Construct of SSHBlock."""
        conv3x3 = self.conv3x3(x)

        conv5x5_1 = self.conv5x5_1(x)
        conv5x5 = self.conv5x5_2(conv5x5_1)

        conv7x7_2 = self.conv7x7_2(conv5x5_1)
        conv7x7 = self.conv7x7_3(conv7x7_2)

        out = self.cat((conv3x3, conv5x5, conv7x7))
        out = self.relu(out)

        return out


@ClassFactory.register(ModuleType.NECK)
class RetinaFaceNeck(nn.Cell):
    """The neck of RetinaFace

     Note:
         backbone = ResNet50

     Args:
         backbone_shape: List. Darknet output channels shape.
         backbone: Cell. Backbone Network.
         out_channel: Integer. Output channel.

     Returns:
        Tuple, tuple of output tensor,(f1,f2,f3).

     Examples:
         RetinaFaceNeck(in_channels=[ 512, 1024, 2048 ],
                out_channel=256)
     """

    def __init__(self, in_channels, out_channels):
        super(RetinaFaceNeck, self).__init__()
        self.retinaface_fpn = RetinafaceFPN(in_channels, out_channels)
        self.ssh1 = SSHBlock(out_channels, out_channels)
        self.ssh2 = SSHBlock(out_channels, out_channels)
        self.ssh3 = SSHBlock(out_channels, out_channels)

    def construct(self, inputs):
        """Construct of RetinaFaceNeck."""
        outputs = self.retinaface_fpn(inputs)
        f1 = self.ssh1(outputs[0])
        f2 = self.ssh2(outputs[1])
        f3 = self.ssh3(outputs[2])
        outs = (f1, f2, f3)
        return outs
