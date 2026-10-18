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
"""Squeeze Excite Module."""

from typing import Union

import mindspore.nn as nn
from mindspore import Tensor
from mindspore.ops import operations as P


class Swish(nn.Cell):
    """
    swish activation function.

    Args:
        None

    Return:
        Tensor

    Example:
        >>> x = Tensor(((20, 16), (50, 50)), mindspore.float32)
        >>> Swish()(x)
    """

    def __init__(self) -> None:
        super(Swish, self).__init__()
        self.sigmoid = nn.Sigmoid()

    def construct(self, x) -> Tensor:
        """Swish construct."""
        return x * self.sigmoid(x)


class SqueezeExcite(nn.Cell):
    """
    squeeze-excite implementation.

    Args:
        in_chs (int): Number of channels of input.
        reduce_chs (int, optional): Number of squeeze channels. Default: None.
        act_fn (Union[str, nn.Cell]): The activation of conv_expand: Default: Swish.
        gate_fn (Union[str, nn.Cell]): The activation of conv_reduce: Default: "sigmod".

    Returns:
        Tensor

    Examples:
        >>> x = Tensor(((20, 16), (50, 50)), mindspore.float32)
        >>> SqueezeExcite(3, 3, "sigmod")(x)
    """

    def __init__(self,
                 in_chs: int,
                 reduce_chs: int,
                 act_fn: Union[str, nn.Cell] = Swish,
                 gate_fn: Union[str, nn.Cell] = "sigmoid"
                 ) -> None:
        super(SqueezeExcite, self).__init__()
        self.act_fn = nn.get_activation(act_fn) if isinstance(act_fn, str) else act_fn()
        self.gate_fn = nn.get_activation(gate_fn) if isinstance(gate_fn, str) else gate_fn()
        reduce_chs = reduce_chs or in_chs
        self.conv_reduce = nn.Conv2d(in_channels=in_chs,
                                     out_channels=reduce_chs,
                                     kernel_size=1,
                                     has_bias=True,
                                     pad_mode='pad'
                                     )
        self.conv_expand = nn.Conv2d(in_channels=reduce_chs,
                                     out_channels=in_chs,
                                     kernel_size=1,
                                     has_bias=True,
                                     pad_mode='pad'
                                     )
        self.avg_global_pool = P.ReduceMean(keep_dims=True)

    def construct(self, x) -> Tensor:
        """Squeeze-excite construct."""
        x_se = self.avg_global_pool(x, (2, 3))
        x_se = self.conv_reduce(x_se)
        x_se = self.act_fn(x_se)
        x_se = self.conv_expand(x_se)
        x_se = self.gate_fn(x_se)
        x = x * x_se
        return x
