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
"""Inception3d Module."""

from mindspore.ops import operations as P
import mindspore.nn as nn
from mindvision.engine.class_factory import ClassFactory, ModuleType


class Unit3D(nn.Cell):
    """
    Unit3D definition.

    Args:
        in_channels (int):  The number of channels of input frame images.
        out_channels (int):  The number of channels of output frame images.
        kernel_shape (tuple): The size of the kernel .
        stride (tuple): An integer or tuple/list of a single integer, specifying the
            strides of the pooling operation.
        padding (int): Padding size.
        activation_fn (): Activation function applied to each layer.
        use_batch_norm (bool): Whether to use BatchNorm3d.
        has_bias (bool): Whether to use Bias.

    Returns:
        Tensor, output tensor.

    Examples:
        Unit3D(in_channels=in_channels, out_channels=out_channels[0], kernel_shape=(1, 1, 1), padding=0)
    """

    def __init__(self, in_channels,
                 out_channels,
                 kernel_shape=(1, 1, 1),
                 stride=(1, 1, 1),
                 padding=0,
                 activation_fn=nn.ReLU(),
                 use_batch_norm=True,
                 has_bias=False):
        super(Unit3D, self).__init__()
        self.out_channels = out_channels
        self.kernel_shape = kernel_shape
        self.stride = stride
        self.use_batch_norm = use_batch_norm
        self.activation_fn = activation_fn
        self.has_bias = has_bias
        self.padding = padding
        self.conv3d = nn.Conv3d(in_channels=in_channels,
                                out_channels=self.out_channels,
                                kernel_size=self.kernel_shape,
                                stride=self.stride,
                                padding=0,
                                has_bias=self.has_bias)

        if self.use_batch_norm:
            self.bn = nn.BatchNorm3d(
                self.out_channels, eps=0.001, momentum=0.01)

    def construct(self, x):
        x = self.conv3d(x)
        if self.use_batch_norm:
            x = self.bn(x)
        if not self.activation_fn:
            x = self.activation_fn(x)
        return x


@ClassFactory.register(ModuleType.BACKBONE)
class Inception3dModule(nn.Cell):
    """
    Inception3dModule definition.

    Args:
        in_channels (int):  The number of channels of input frame images.
        out_channels (int): The number of channels of output frame images.

    Returns:
        Tensor, output tensor.

    Examples:
        Inception3dModule(in_channels=3, out_channels=3)
    """

    def __init__(self, in_channels, out_channels):
        super(Inception3dModule, self).__init__()
        self.cat = P.Concat(axis=1)
        self.b0 = Unit3D(
            in_channels=in_channels,
            out_channels=out_channels[0],
            kernel_shape=(1, 1, 1),
            padding=0)
        self.b1a = Unit3D(
            in_channels=in_channels,
            out_channels=out_channels[1],
            kernel_shape=(1, 1, 1),
            padding=0)
        self.b1b = Unit3D(
            in_channels=out_channels[1],
            out_channels=out_channels[2],
            kernel_shape=(3, 3, 3))
        self.b2a = Unit3D(
            in_channels=in_channels,
            out_channels=out_channels[3],
            kernel_shape=(1, 1, 1),
            padding=0)
        self.b2b = Unit3D(
            in_channels=out_channels[3],
            out_channels=out_channels[4],
            kernel_shape=(3, 3, 3))
        self.b3a = P.MaxPool3D(
            kernel_size=(3, 3, 3),
            strides=(1, 1, 1),
            pad_mode="same")
        self.b3b = Unit3D(
            in_channels=in_channels,
            out_channels=out_channels[5],
            kernel_shape=(1, 1, 1),
            padding=0)

    def construct(self, x):
        b0 = self.b0(x)
        b1 = self.b1b(self.b1a(x))
        b2 = self.b2b(self.b2a(x))
        b3 = self.b3b(self.b3a(x))
        return self.cat((b0, b1, b2, b3))
