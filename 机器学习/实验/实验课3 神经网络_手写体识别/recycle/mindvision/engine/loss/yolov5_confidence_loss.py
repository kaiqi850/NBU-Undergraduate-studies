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
"""Softmax Cross Entropy with Logits with label smoothing"""

import mindspore.nn as nn
from mindspore.ops import operations as P

from mindvision.engine.class_factory import ClassFactory, ModuleType

@ClassFactory.register(ModuleType.LOSS)
class YOLOv5ConfidenceLoss(nn.Cell):
    """Loss for confidence."""

    def __init__(self):
        super(YOLOv5ConfidenceLoss, self).__init__()
        self.cross_entropy = P.SigmoidCrossEntropyWithLogits()
        self.reduce_sum = P.ReduceSum()

    def construct(self, object_mask, predict_confidence, ignore_mask):
        confidence_loss = self.cross_entropy(predict_confidence, object_mask)
        confidence_loss = object_mask * confidence_loss + (1 - object_mask) * confidence_loss * ignore_mask
        confidence_loss = self.reduce_sum(confidence_loss, ())
        return confidence_loss
