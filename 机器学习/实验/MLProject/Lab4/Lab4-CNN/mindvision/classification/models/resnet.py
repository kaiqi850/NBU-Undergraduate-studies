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
"""Resnet."""

from typing import Any, Type, Union, List

from mindvision.classification.models.backbones import ResidualBlockBase, ResidualBlock, ResNet
from mindvision.classification.models.classifiers import BaseClassifier
from mindvision.classification.models.head import DenseHead
from mindvision.classification.models.neck import GlobalAvgPooling
from mindvision.classification.utils.model_urls import model_urls
from mindvision.utils.load_pretrained_model import LoadPretrainedModel

__all__ = [
    'resnet18',
    'resnet34',
    'resnet50',
    'resnet101',
    'resnet152'
]


def _resnet(arch: str,
            block: Type[Union[ResidualBlockBase, ResidualBlock]],
            layers: List[int],
            num_classes: int,
            pretrained: bool,
            input_channel: int,
            **kwargs: Any
            ) -> ResNet:
    """ResNet architecture."""
    backbone = ResNet(block, layers, **kwargs)
    neck = GlobalAvgPooling()
    head = DenseHead(input_channel=input_channel, num_classes=num_classes)
    model = BaseClassifier(backbone, neck, head)

    if pretrained:
        # Download the pre-trained checkpoint file from url, and load
        # checkpoint file.
        LoadPretrainedModel(model, model_urls[arch]).run()

    return model


def resnet18(
        num_classes: int = 1000,
        pretrained: bool = False,
        **kwargs: Any) -> ResNet:
    """
    ResNet18 architecture.

    Args:
        num_classes (int): Number of classification. Default: 1000.
        pretrained (bool): Download and load the pre-trained model. Default: False.

    Returns:
        ResNet

    Examples:
        >>> resnet18(num_classes=10, pretrained=True, **kwargs)
    """
    return _resnet(
        "resnet18", ResidualBlockBase, [
            2, 2, 2, 2], num_classes, pretrained, 512, **kwargs)


def resnet34(
        num_classes: int = 1000,
        pretrained: bool = False,
        **kwargs: Any) -> ResNet:
    """
    ResNet34 architecture.

    Args:
        num_classes (int): Number of classification. Default: 1000.
        pretrained (bool): Download and load the pre-trained model. Default: False.

    Returns:
        ResNet

    Examples:
        >>> resnet34(num_classes=10, pretrained=True, **kwargs)
    """
    return _resnet(
        "resnet34", ResidualBlockBase, [
            3, 4, 6, 3], num_classes, pretrained, 512, **kwargs)


def resnet50(
        num_classes: int = 1000,
        pretrained: bool = False,
        **kwargs: Any) -> ResNet:
    """
    ResNet50 architecture.

    Args:
        num_classes (int): Number of classification. Default: 1000.
        pretrained (bool): Download and load the pre-trained model. Default: False.

    Returns:
        ResNet

    Examples:
        >>> resnet50(num_classes=10, pretrained=True, **kwargs)
    """
    return _resnet(
        "resnet50", ResidualBlock, [
            3, 4, 6, 3], num_classes, pretrained, 2048, **kwargs)


def resnet101(
        num_classes: int = 1000,
        pretrained: bool = False,
        **kwargs: Any) -> ResNet:
    """
    ResNet101 architecture.

    Args:
        num_classes (int): Number of classification. Default: 1000.
        pretrained (bool): Download and load the pre-trained model. Default: False.

    Returns:
        ResNet

    Examples:
        >>> resnet101(num_classes=10, pretrained=True, **kwargs)
    """
    return _resnet(
        "resnet101", ResidualBlock, [
            3, 4, 23, 3], num_classes, pretrained, 2048, **kwargs)


def resnet152(
        num_classes: int = 1000,
        pretrained: bool = False,
        **kwargs: Any) -> ResNet:
    """
    ResNet152 architecture.

    Args:
        num_classes (int): Number of classification. Default: 1000.
        pretrained (bool): Download and load the pre-trained model. Default: False.

    Returns:
        ResNet

    Examples:
        >>> resnet152(num_classes=10, pretrained=True, **kwargs)
    """
    return _resnet(
        "resnet152", ResidualBlock, [
            3, 8, 36, 3], num_classes, pretrained, 2048, **kwargs)
