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
""" Calculate MSE. TODO: merge the loss into mindspore.nn.loss and clean these folder."""

import mindspore.nn as nn
from mindspore.ops import operations as P

from mindvision.engine.class_factory import ClassFactory, ModuleType


@ClassFactory.register(ModuleType.LOSS)
class MseLoss(nn.Cell):
    """The mse loss.

    Args:
        reduction (str) : `mean` or `sum`

    """

    def __init__(self, reduction="mean", loss_weight=1.0):
        """Constructor for MseLoss"""
        super(MseLoss, self).__init__()
        self.reduce_sum = P.ReduceSum()
        self.loss_weight = loss_weight
        self.square = P.Square()
        self.reduction = reduction

    def construct(self, predict, groud_truth, weight=None, normalize=None):
        loss = self.square(predict - groud_truth)
        if weight is not None:
            loss = weight * loss
        if self.reduction == "mean" and normalize is not None:
            loss = loss / normalize

        loss = self.reduce_sum(loss, ())
        loss = self.loss_weight * loss
        return loss
