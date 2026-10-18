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
"""LeNet."""

from typing import Any

from mindvision.classification.models.backbones import LeNet5
from mindvision.classification.models.classifiers import BaseClassifier
from mindvision.classification.utils.model_urls import model_urls
from mindvision.utils.load_pretrained_model import LoadPretrainedModel

__all__ = ['lenet']


def lenet(num_classes: int = 10, pretrained: bool = False, ckpt_file=None, **kwargs: Any) -> LeNet5:
    """LeNet structure."""
    backbone = LeNet5(num_classes=num_classes, **kwargs)
    model = BaseClassifier(backbone)

    if pretrained and not ckpt_file:
        # Download the pre-trained checkpoint file from url, and load checkpoint file.
        arch = "lenet"
        LoadPretrainedModel(model, model_urls[arch]).run()
    elif ckpt_file:
        # Just load checkpoint file.
        LoadPretrainedModel(model, ckpt_file).run()

    return model
