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
"""Mobilenet_v2."""

from typing import Any

from mindvision.classification.models.backbones import MobileNetV2
from mindvision.classification.models.classifiers import BaseClassifier
from mindvision.classification.models.head import ConvHead
from mindvision.classification.models.neck import GlobalAvgPooling
from mindvision.classification.models.utils import make_divisible
from mindvision.classification.utils.model_urls import model_urls
from mindvision.utils.load_pretrained_model import LoadPretrainedModel

__all__ = ['mobilenet_v2']


def mobilenet_v2(num_classes: int = 1001,
                 alpha: float = 1.0,
                 round_nearest: int = 8,
                 pretrained: bool = False,
                 resize: int = 224,
                 **kwargs: Any) -> MobileNetV2:
    """Mobilenet v2 structure."""
    backbone = MobileNetV2(alpha=alpha, round_nearest=round_nearest, **kwargs)
    neck = GlobalAvgPooling(keep_dims=True)
    inp_channel = make_divisible(1280 * max(1.0, alpha), round_nearest)
    head = ConvHead(input_channel=inp_channel, num_classes=num_classes)
    model = BaseClassifier(backbone, neck, head)

    if pretrained:
        # Download the pre-trained checkpoint file from url, and load
        # checkpoint file.
        arch = "mobilenet_v2_" + str(alpha) + "_" + str(resize)
        LoadPretrainedModel(model, model_urls[arch]).run()

    return model
