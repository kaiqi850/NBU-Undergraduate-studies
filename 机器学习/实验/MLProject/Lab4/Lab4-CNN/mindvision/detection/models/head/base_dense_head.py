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
""" Base Dense Head """

from abc import abstractmethod

import mindspore as ms
import mindspore.nn as nn
from mindspore.ops import functional as F
from mindspore.ops import operations as P


class BaseDenseHead(nn.Cell):
    """ The base dense head class. """

    @abstractmethod
    def loss(self, *args, **kwargs):
        """Dense-net Loss."""
        return

    def construct_train(self, feats, *args, **kwargs):
        """Model Train."""
        image = args[0]
        if self.training:
            input_shape = P.Cast()(F.tuple_to_array(image.shape[2:4]), ms.float32)
            input_shape = input_shape * 2
        else:
            input_shape = args[1]

        out = self(feats, input_shape)

        if self.training:
            return self.loss(out, input_shape, *args, **kwargs)

        return out
