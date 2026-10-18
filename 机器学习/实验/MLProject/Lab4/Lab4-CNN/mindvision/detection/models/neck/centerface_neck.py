# Copyright 2020-21 Huawei Technologies Co., Ltd
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
"""centerface FPN"""

import mindspore.nn as nn

from mindvision.engine.class_factory import ClassFactory, ModuleType


def conv1x1(in_channels, out_channels, stride=1, padding=0, has_bias=False):
    """conv1x1"""
    return nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, has_bias=has_bias,
                     padding=padding, pad_mode="pad")


def conv3x3(in_channels, out_channels, stride=1, padding=1, has_bias=False):
    """conv3x3"""
    return nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, has_bias=has_bias,
                     padding=padding, pad_mode="pad")


def convtranspose2x2(in_channels, out_channels, has_bias=False):  # Davinci devices only support 'groups=1'
    """convtranspose2x2"""
    return nn.Conv2dTranspose(in_channels, out_channels, kernel_size=2, stride=2, has_bias=has_bias,
                              weight_init='normal', bias_init='zeros')


class IDAUp(nn.Cell):
    """
    IDA Module.
    """

    def __init__(self, out_dim, channel):
        super(IDAUp, self).__init__()
        self.out_dim = out_dim
        self.up = nn.SequentialCell([
            convtranspose2x2(out_dim, out_dim, has_bias=False),
            nn.BatchNorm2d(out_dim, eps=0.001, momentum=0.9).add_flags_recursive(fp32=True),
            nn.ReLU()])
        self.conv = nn.SequentialCell([
            conv1x1(channel, out_dim),
            nn.BatchNorm2d(out_dim, eps=0.001, momentum=0.9).add_flags_recursive(fp32=True),
            nn.ReLU()])

    def construct(self, x0, x1):
        """IDAUp_output"""
        x = self.up(x0)
        y = self.conv(x1)
        out = x + y
        return out


class MobileNetUp(nn.Cell):
    """
    Mobilenet module.
    """

    def __init__(self, channels, out_dim):
        super(MobileNetUp, self).__init__()
        channels = channels[::-1]
        self.conv = nn.SequentialCell([
            conv1x1(channels[0], out_dim),
            nn.BatchNorm2d(out_dim, eps=0.001).add_flags_recursive(fp32=True),
            nn.ReLU()])
        self.conv_last = nn.SequentialCell([
            conv3x3(out_dim, out_dim),
            nn.BatchNorm2d(out_dim, eps=1e-5, momentum=0.99).add_flags_recursive(fp32=True),
            nn.ReLU()])

        self.up1 = IDAUp(out_dim, channels[1])
        self.up2 = IDAUp(out_dim, channels[2])
        self.up3 = IDAUp(out_dim, channels[3])

    def construct(self, x1, x2, x3, x4):  # tuple/list can be type of input of a subnet
        """MobileNetUp_output"""
        x = self.conv(x4)  # top_layer, change outdim

        x = self.up1(x, x3)
        x = self.up2(x, x2)
        x = self.up3(x, x1)
        x = self.conv_last(x)
        return x


@ClassFactory.register(ModuleType.NECK)
class CenterFaceNeck(nn.Cell):
    """centerface neck"""

    def __init__(self, in_channels, out_dim):
        super(CenterFaceNeck, self).__init__()
        self.channels = in_channels
        self.out_dim = out_dim
        self.dla_up = MobileNetUp(self.channels, self.out_dim)

    def construct(self, inputs):
        """CenterFaceNeck_output"""
        x = self.dla_up(inputs[0], inputs[1], inputs[2], inputs[3])

        return x
