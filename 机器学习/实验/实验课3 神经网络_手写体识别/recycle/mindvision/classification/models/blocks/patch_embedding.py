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
"""Path Embedding module."""

from mindspore import nn
from mindspore.ops import operations as P

from mindvision.check_param import Rel, Validator


class PatchEmbedding(nn.Cell):
    """
    Path embedding layer for ViT. First rearrange b c (h p) (w p) -> b (h w) (p p c).

    Args:
        image_size (int): Input image size. Default: 224.
        patch_size (int): Patch size of image. Default: 16.
        embed_dim (int): The dimension of embedding. Default: 768.
        input_channels (int): The number of input channel. Default: 3.

    Returns:
        Tensor, output tensor.

    Examples:
        >>> ops = PathEmbedding(224, 16, 768, 3)
    """
    MIN_NUM_PATCHES = 4

    def __init__(self,
                 image_size: int = 224,
                 patch_size: int = 16,
                 embed_dim: int = 768,
                 input_channels: int = 3):
        super(PatchEmbedding, self).__init__()
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_patches = (image_size // patch_size) ** 2
        Validator.check_int(
            self.num_patches, self.MIN_NUM_PATCHES, Rel.GE, "num patches")
        self.conv = nn.Conv2d(input_channels, embed_dim, kernel_size=patch_size, stride=patch_size, has_bias=True)
        self.reshape = P.Reshape()
        self.transpose = P.Transpose()

    def construct(self, x):
        """Path Embedding construct."""
        x = self.conv(x)
        b, c, h, w = x.shape
        x = self.reshape(x, (b, c, h * w))
        x = self.transpose(x, (0, 2, 1))

        return x
