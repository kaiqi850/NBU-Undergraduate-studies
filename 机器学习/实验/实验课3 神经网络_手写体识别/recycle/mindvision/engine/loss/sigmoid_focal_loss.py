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
"""Sigmoid focal-loss. TODO: merge the loss into mindspore.nn.loss and clean these folder."""

import mindspore.common.dtype as mstype
import mindspore.nn as nn
from mindspore import Tensor
from mindspore.ops import functional as F
from mindspore.ops import operations as P

from mindvision.engine.class_factory import ClassFactory, ModuleType


@ClassFactory.register(ModuleType.LOSS)
class SigmoidFocalClassificationLoss(nn.Cell):
    """"
    Sigmoid focal-loss for classification.

    Args:
        gamma (float): Hyper-parameter to balance the easy and hard examples. Default: 2.0
        alpha (float): Hyper-parameter to balance the positive and negative example. Default: 0.25

    Returns:
        Tensor, the focal loss.
    """

    def __init__(self, gamma=2.0, alpha=0.25):
        super(SigmoidFocalClassificationLoss, self).__init__()
        self.sigmiod_cross_entropy = P.SigmoidCrossEntropyWithLogits()
        self.sigmoid = P.Sigmoid()
        self.pow = P.Pow()
        self.onehot = P.OneHot()
        self.reduce_sum = P.ReduceSum()
        self.on_value = Tensor(1.0, mstype.float32)
        self.off_value = Tensor(0.0, mstype.float32)
        self.gamma = gamma
        self.alpha = alpha

    def construct(self, logits, label):
        """construct for sigmoid focal-loss"""
        label = self.onehot(label, F.shape(logits)[-1], self.on_value, self.off_value)
        sigmiod_cross_entropy = self.sigmiod_cross_entropy(logits, label)
        sigmoid = self.sigmoid(logits)
        label = F.cast(label, mstype.float32)
        p_t = label * sigmoid + (1 - label) * (1 - sigmoid)
        modulating_factor = self.pow(1 - p_t, self.gamma)
        alpha_weight_factor = label * self.alpha + (1 - label) * (1 - self.alpha)
        focal_loss = modulating_factor * alpha_weight_factor * sigmiod_cross_entropy
        focal_loss = self.reduce_sum(focal_loss, (1, 2))
        return focal_loss
