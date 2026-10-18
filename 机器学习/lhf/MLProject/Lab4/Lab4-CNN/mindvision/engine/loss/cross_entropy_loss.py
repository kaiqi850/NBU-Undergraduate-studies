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
"""Cross entropy loss.  TODO: merge the loss into mindspore.nn.loss and clean these folder."""

import mindspore.common.dtype as mstype
import mindspore.nn as nn
from mindspore.ops import operations as P

from mindvision.engine.class_factory import ClassFactory, ModuleType


@ClassFactory.register(ModuleType.LOSS)
class CrossEntropyLoss(nn.Cell):
    """Loss for x and y."""

    def __init__(self, use_sigmoid=False, reduction="mean", loss_weight=1.0):
        super(CrossEntropyLoss, self).__init__()
        self.reduce_sum = P.ReduceSum()
        self.loss_weight = loss_weight
        self.reduction = reduction
        self.use_sigmoid = use_sigmoid
        if use_sigmoid:
            self.cross_entropy = P.SigmoidCrossEntropyWithLogits()
        else:
            self.cross_entropy = P.SoftmaxCrossEntropyWithLogits()

    def construct(self, predict, groud_truth, weight=1.0, normalizer=1.0):
        """Construct of CrossEntropy."""
        if self.use_sigmoid:
            loss = self.cross_entropy(predict, groud_truth)
        else:
            loss, _ = self.cross_entropy(predict, groud_truth)
        loss = P.Cast()(loss, mstype.float32)
        loss = loss * weight
        if self.reduction == "mean":
            loss = self.reduce_sum(loss, ()) / normalizer
        elif self.reduction == "sum":
            loss = self.reduce_sum(loss, ())

        loss = loss * self.loss_weight
        return loss
