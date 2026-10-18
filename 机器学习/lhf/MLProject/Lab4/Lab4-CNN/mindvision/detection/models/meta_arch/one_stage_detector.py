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
"""One stage detector."""

from mindvision.detection.models.builder import build_backbone, build_neck, build_head
from mindvision.detection.models.meta_arch.base_detector import BaseDetector
from mindvision.engine.utils.config import Config


class OneStageDetector(BaseDetector):
    """Base Class of one-stage detector.

    Args:
        config (Config) : Detector Config dict

    Examples:
    """

    def __init__(self, **kwargs):
        """Constructor for OneStageDetector"""
        super(OneStageDetector, self).__init__()
        config = Config(**kwargs)

        if config.backbone is None:
            raise ValueError("Backbone cannot be None!")
        self.backbone = build_backbone(config.backbone)
        if config.neck is not None:
            self.neck = build_neck(config.neck)
        if config.bbox_head is None:
            raise ValueError("Bbox head cannot be None!")
        self.bbox_head = build_head(config.bbox_head)
        self.cfg = config

    def construct(self, *args, **kwargs):
        """Construct model."""
        image = args[0]
        x = self.backbone(image)
        if self.has_neck:
            x = self.neck(x)
        if self.training:
            x = self.bbox_head.construct_train(x, *args, **kwargs)
        else:
            x = self.bbox_head.construct_test(x, *args, **kwargs)
        return x
