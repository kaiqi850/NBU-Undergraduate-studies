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
"""Pooling neck."""

import mindspore.nn as nn
from mindspore.ops import operations as P

from mindvision.engine.class_factory import ClassFactory, ModuleType


@ClassFactory.register(ModuleType.NECK)
class GlobalAvgPooling(nn.Cell):
    """
    Global avg pooling definition.

    Args:

    Returns:
        Tensor, output tensor.

    Examples:
        >>> GlobalAvgPooling()
    """

    def __init__(self,
                 keep_dims: bool = False
                 ) -> None:
        super(GlobalAvgPooling, self).__init__()
        self.mean = P.ReduceMean(keep_dims=keep_dims)

    def construct(self, x):
        x = self.mean(x, (2, 3))
        return x


@ClassFactory.register(ModuleType.NECK)
class AvgPooling(nn.Cell):
    """
    Applies a 1D/2D average pooling over an input Tensor.

    Args:
        dim (int) : The dimension of the pooling kernel.
        kernel_size (Union[int, tuple[int]]): The size of kernel used to take the average value.
            The data type of kernel_size must be int and the value represents the height and width,
            or a tuple of two int numbers that represent height and width respectively.
            Default: 1.
        stride (Union[int, tuple[int]]): The distance of kernel moving, an int number that represents
            the height and width of movement are both strides, or a tuple of two int numbers that
            represent height and width of movement respectively. Default: 1.
        pad_mode (str): The optional value for pad mode, is "same" or "valid", not case sensitive.
            Default: "valid".

            - same: Adopts the way of completion. The height and width of the output will be the same as
              the input. The total number of padding will be calculated in horizontal and vertical
              directions and evenly distributed to top and bottom, left and right if possible.
              Otherwise, the last extra padding will be done from the bottom and the right side.

            - valid: Adopts the way of discarding. The possible largest height and width of output
              will be returned without padding. Extra pixels will be discarded.

    Returns:
        Tensor, output tensor.

    Examples:
        >>> AvgPooling(dim=1, kernel_size=7, stride=7, pad_mode='valid')
    """

    def __init__(self, dim=1, kernel_size=1, stride=1, pad_mode="valid"):
        super(AvgPooling, self).__init__()
        assert dim in [1, 2], 'AveragePooling dim only support ' \
                              f'{1, 2}, get {dim} instead.'
        if dim == 1:
            self.avg_pooling = nn.AvgPool1d(kernel_size, stride, pad_mode)
        elif dim == 2:
            self.avg_pooling = nn.AvgPool2d(kernel_size, stride, pad_mode)

    def construct(self, x):
        return self.avg_pooling(x)
