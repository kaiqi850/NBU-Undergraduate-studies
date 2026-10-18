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
""" MultilayerDenseHead."""

from typing import Optional, List, Union

import mindspore.nn as nn

from mindvision.engine.class_factory import ClassFactory, ModuleType
from mindvision.classification.models.head import DenseHead


@ClassFactory.register(ModuleType.HEAD)
class MultilayerDenseHead(nn.Cell):
    """
    MultilayerDenseHead architecture.

    Args:
        input_channel (int): The number of input channel.
        num_classes (int): Number of classes.
        mid_channel (list): Number of channels in the hidden fc layers.
        keep_prob (list): Dropout keeping rate, between [0, 1]. E.g. rate=0.9, means dropping out 10% of
        input.
        activation (list): activate function applied to the output. Eg. `ReLU`.

    Returns:
        Tensor, output tensor.
    """

    def __init__(self,
                 input_channel: int,
                 num_classes: int,
                 mid_channel: List[int],
                 keep_prob: List[float],
                 activation: List[Optional[Union[str, nn.Cell]]],
                 ) -> None:
        super(MultilayerDenseHead, self).__init__()
        mid_channel.append(num_classes)
        assert len(mid_channel) == len(activation) == len(keep_prob), "The length of the list should be the same."

        length = len(activation)
        head = []

        for i in range(length):
            linear = DenseHead(input_channel,
                               mid_channel[i],
                               activation=activation[i],
                               keep_prob=keep_prob[i],
                               )
            head.append(linear)
            input_channel = mid_channel[i]

        self.classifier = nn.SequentialCell(head)

    def construct(self, x):
        x = self.classifier(x)

        return x
