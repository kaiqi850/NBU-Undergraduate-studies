# Copyright 2022 Huawei Technologies Co., Ltd
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
"""EfficientNet Architecture"""

from typing import Any
from functools import partial

import mindspore.nn as nn

from mindvision.classification.models.head import DenseHead
from mindvision.classification.utils.model_urls import model_urls
from mindvision.utils.load_pretrained_model import LoadPretrainedModel
from mindvision.classification.models.classifiers import BaseClassifier
from mindvision.classification.models.backbones import EfficientNet

__all__ = [
    "efficientnet_b0",
    "efficientnet_b1",
    "efficientnet_b2",
    "efficientnet_b3",
    "efficientnet_b4",
    "efficientnet_b5",
    "efficientnet_b6",
    "efficientnet_b7",
]


def _efficientnet(
        arch: str,
        width_mult: float,
        depth_mult: float,
        dropout: float,
        input_channel: int,
        num_classes: int,
        pretrained: bool,
        **kwargs: Any,
        ) -> EfficientNet:
    """EfficientNet architecture."""

    backbone = EfficientNet(width_mult, depth_mult, **kwargs)
    head = DenseHead(input_channel, num_classes, keep_prob=1-dropout)
    model = BaseClassifier(backbone, head=head)

    if pretrained:
        # Download the pre-trained checkpoint file from url, and load
        # checkpoint file.
        LoadPretrainedModel(model, model_urls[arch]).run()
    return model


def efficientnet_b0(
        num_classes: int = 1000,
        pretrained: bool = False,
        **kwargs: Any
        ) -> EfficientNet:
    """
    EfficientNet B0 architecture.

    Args:
        num_classes (int): Numbers of classes. Default: 1000.
        pretrained (bool): If True, returns a model pre-trained on ImageNet. Default: False.

    Returns:
        EfficientNet

    Examples:
        >>> efficientnet_b0(1000, True)
    """
    return _efficientnet("efficientnet_b0", 1.0, 1.0, 0.2, 1280, num_classes, pretrained, **kwargs)


def efficientnet_b1(
        num_classes: int = 1000,
        pretrained: bool = False,
        **kwargs: Any
        ) -> EfficientNet:
    """
    EfficientNet B1 architecture.

    Args:
        num_classes (int): Numbers of classes. Default: 1000.
        pretrained (bool): If True, returns a model pre-trained on ImageNet. Default: False.

    Returns:
        EfficientNet

    Examples:
        >>> efficientnet_b1(1000, True)
    """
    return _efficientnet("efficientnet_b1", 1.0, 1.1, 0.2, 1280, num_classes, pretrained, **kwargs)


def efficientnet_b2(
        num_classes: int = 1000,
        pretrained: bool = False,
        **kwargs: Any
        ) -> EfficientNet:
    """
    EfficientNet B2 architecture.

    Args:
        num_classes (int): Numbers of classes. Default: 1000.
        pretrained (bool): If True, returns a model pre-trained on ImageNet. Default: False.

    Returns:
        EfficientNet

    Examples:
        >>> efficientnet_b2(1000, True)
    """
    return _efficientnet("efficientnet_b2", 1.1, 1.2, 0.3, 1408, num_classes, pretrained, **kwargs)


def efficientnet_b3(
        num_classes: int = 1000,
        pretrained: bool = False,
        **kwargs: Any
        ) -> EfficientNet:
    """
    EfficientNet B3 architecture.

    Args:
        num_classes (int): Numbers of classes. Default: 1000.
        pretrained (bool): If True, returns a model pre-trained on ImageNet. Default: False.

    Returns:
        EfficientNet

    Examples:
        >>> efficientnet_b3(1000, True)
    """
    return _efficientnet("efficientnet_b3", 1.2, 1.4, 0.3, 1536, num_classes, pretrained, **kwargs)


def efficientnet_b4(
        num_classes: int = 1000,
        pretrained: bool = False,
        **kwargs: Any
        ) -> EfficientNet:
    """
    EfficientNet B4 architecture.

    Args:
        num_classes (int): Numbers of classes. Default: 1000.
        pretrained (bool): If True, returns a model pre-trained on ImageNet. Default: False.

    Returns:
        EfficientNet

    Examples:
        >>> efficientnet_b4(1000, True)
    """
    return _efficientnet("efficientnet_b4", 1.4, 1.8, 0.4, 1792, num_classes, pretrained, **kwargs)


def efficientnet_b5(
        num_classes: int = 1000,
        pretrained: bool = False,
        **kwargs: Any
        ) -> EfficientNet:
    """
    EfficientNet B5 architecture.

    Args:
        num_classes (int): Numbers of classes. Default: 1000.
        pretrained (bool): If True, returns a model pre-trained on ImageNet. Default: False.

    Returns:
        EfficientNet

    Examples:
        >>> efficientnet_b5(1000, True)
    """
    return _efficientnet(
        "efficientnet_b5",
        1.6,
        2.2,
        0.4,
        2048,
        num_classes,
        pretrained,
        norm_layer=partial(nn.BatchNorm2d, eps=0.001, momentum=0.99),
        **kwargs,
    )


def efficientnet_b6(
        num_classes: int = 1000,
        pretrained: bool = False,
        **kwargs: Any
        ) -> EfficientNet:
    """
    EfficientNet B6 architecture.

    Args:
        num_classes (int): Numbers of classes. Default: 1000.
        pretrained (bool): If True, returns a model pre-trained on ImageNet. Default: False.

    Returns:
        EfficientNet

    Examples:
        >>> efficientnet_b6(1000, True)
    """
    return _efficientnet(
        "efficientnet_b6",
        1.8,
        2.6,
        0.5,
        2304,
        num_classes,
        pretrained,
        norm_layer=partial(nn.BatchNorm2d, eps=0.001, momentum=0.99),
        **kwargs,
    )


def efficientnet_b7(
        num_classes: int = 1000,
        pretrained: bool = False,
        **kwargs: Any
        ) -> EfficientNet:
    """
    EfficientNet B7 architecture.

    Args:
        num_classes (int): Numbers of classes. Default: 1000.
        pretrained (bool): If True, returns a model pre-trained on ImageNet. Default: False.

    Returns:
        EfficientNet

    Examples:
        >>> efficientnet_b7(1000, True)
    """
    return _efficientnet(
        "efficientnet_b7",
        2.0,
        3.1,
        0.5,
        2560,
        num_classes,
        pretrained,
        norm_layer=partial(nn.BatchNorm2d, eps=0.001, momentum=0.99),
        **kwargs,
    )
