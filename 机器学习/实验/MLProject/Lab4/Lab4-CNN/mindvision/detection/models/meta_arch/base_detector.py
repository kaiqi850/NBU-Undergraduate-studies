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
"""Base detector define."""

from mindspore import nn


class BaseDetector(nn.Cell):
    """Base detector class."""

    def init_weights(self, config):
        """Model weights Initialization."""
        raise NotImplementedError("Should implement init_weight method!")

    def get_trainable_params(self):
        """Get trainable parameters."""
        return self.trainable_params()

    @property
    def has_neck(self):
        """Check model neck."""
        return hasattr(self, 'neck') and self.neck is not None

    @property
    def has_roi_head(self):
        """Check roi head."""
        return hasattr(self, 'roi_head') and self.roi_head is not None

    @property
    def has_bbox_head(self):
        """Check model bbox head."""
        return hasattr(self, 'bbox_head') and self.bbox_head is not None

    def construct(self, *args):
        """Construct model."""
        if self.training:
            loss = self.construct_train(*args)
            return loss
        return self.construct_test(*args)
