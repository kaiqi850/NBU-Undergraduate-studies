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
"""ResNet Full X."""

from models.backbone.resnet import ResNet

from mindvision.engine.class_factory import ClassFactory, ModuleType


@ClassFactory.register(ModuleType.BACKBONE)
class ResNeXt(ResNet):
    """
    ResNetPlus architecture.

    Args:
        depth (int): ResNet depth.
        strides (list):  Stride size in each layer.

    Returns:
        Tensor, output tensor.

    Examples:
        >>> ResNeXt(50, [1, 2, 2, 2])
    """

    def __init__(self, **kwargs):
        ResNet.__init__(self, **kwargs)


def resnext50_32x4d():
    """
    Get ResNeXt50 neural network.

    Returns:
        Cell, cell instance of ResNeXt50 neural network.

    Examples:
        >>> net = resnext50_32x4d()
    """
    return ResNeXt(depth=50,
                   strides=[1, 2, 2, 2],
                   in_channels=[64, 256, 512, 1024],
                   out_channels=[256, 512, 1024, 2048],
                   width_per_group=4,
                   groups=32,
                   use_group=True)


def resnext50_64x4d():
    """
    Get ResNeXt50 neural network.

    Returns:
        Cell, cell instance of ResNeXt50 neural network.

    Examples:
        >>> net = resnext50_32x4d()
    """
    return ResNeXt(depth=50,
                   strides=[1, 2, 2, 2],
                   in_channels=[64, 256, 512, 1024],
                   out_channels=[256, 512, 1024, 2048],
                   width_per_group=4,
                   groups=64,
                   use_group=True)


def se_resnext50_32x4d():
    """
    Get SE_ResNeXt50 neural network.

    Returns:
        Cell, cell instance of ResNeXt50 neural network.

    Examples:
        >>> net = se_resnext50_32x4d()
    """
    return ResNeXt(depth=50,
                   strides=[1, 2, 2, 2],
                   in_channels=[64, 256, 512, 1024],
                   out_channels=[256, 512, 1024, 2048],
                   width_per_group=4,
                   groups=32,
                   use_se=True,
                   use_group=True)


def se_resnext50_64x4d():
    """
    Get SE_ResNeXt50 neural network.

    Returns:
        Cell, cell instance of ResNeXt50 neural network.

    Examples:
        >>> net = se_resnext50_32x4d()
    """
    return ResNeXt(depth=50,
                   strides=[1, 2, 2, 2],
                   in_channels=[64, 256, 512, 1024],
                   out_channels=[256, 512, 1024, 2048],
                   width_per_group=4,
                   groups=64,
                   use_se=True,
                   use_group=True)


if __name__ == "__main__":
    se_resnext50_32x4d = se_resnext50_32x4d()
