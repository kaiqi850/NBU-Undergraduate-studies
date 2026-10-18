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
"""Anchor generator."""

import mindspore as ms
import mindspore.common.dtype as mstype
import numpy as np
from mindspore import Tensor
from mindspore.ops import operations as P

from mindvision.engine.class_factory import ClassFactory, ModuleType


@ClassFactory.register(ModuleType.ANCHOR_GENERATOR)
class AnchorGenerator:
    """Anchor generator for FasterRcnn."""

    def __init__(self, strides, scales, ratios, scale_major=True, ctr=None):
        """Anchor generator init method."""
        self.base_sizes = strides
        self.scales = np.array(scales)
        self.ratios = np.array(ratios)
        self.scale_major = scale_major
        self.ctr = ctr

    def _gen_base_anchors(self, h, w):
        """Generate a single anchor."""
        if self.ctr is None:
            x_ctr = 0.5 * (w - 1)
            y_ctr = 0.5 * (h - 1)
        else:
            x_ctr, y_ctr = self.ctr

        h_ratios = np.sqrt(self.ratios)
        w_ratios = 1 / h_ratios
        if self.scale_major:
            ws = (w * w_ratios[:, None] * self.scales[None, :]).reshape(-1)
            hs = (h * h_ratios[:, None] * self.scales[None, :]).reshape(-1)
        else:
            ws = (w * self.scales[:, None] * w_ratios[None, :]).reshape(-1)
            hs = (h * self.scales[:, None] * h_ratios[None, :]).reshape(-1)

        base_anchors = np.stack(
            [
                x_ctr - 0.5 * (ws - 1), y_ctr - 0.5 * (hs - 1),
                x_ctr + 0.5 * (ws - 1), y_ctr + 0.5 * (hs - 1)
            ],
            axis=-1
        ).round()

        return base_anchors

    def grid_anchors(self, featmap_size, stride=16):
        """Generate anchor list."""
        base_anchors = self._gen_base_anchors(stride, stride)

        feat_h, feat_w = featmap_size
        shift_x = np.arange(0, feat_w) * stride
        shift_y = np.arange(0, feat_h) * stride
        shift_xx, shift_yy = meshgrid(shift_x, shift_y)
        shifts = np.stack([shift_xx, shift_yy, shift_xx, shift_yy], axis=-1)
        shifts = shifts.astype(base_anchors.dtype)
        # first feat_w elements correspond to the first row of shifts
        # add A anchors (1, A, 4) to K shifts (K, 1, 4) to get
        # shifted anchors (K, A, 4), reshape to (K*A, 4)

        all_anchors = base_anchors[None, :, :] + shifts[:, None, :]
        all_anchors = all_anchors.reshape(-1, 4)

        return all_anchors

    def get_anchors(self, featmap_sizes):
        """Get anchors according to feature map sizes.

        Args:
            featmap_sizes (list[tuple]): Multi-level feature map sizes.

        Returns:
            tuple: anchors of each image, valid flags of each image.
        """
        num_levels = len(featmap_sizes)

        # since feature map sizes of all images are the same, we only compute
        # anchors for one time
        multi_level_anchors = ()
        for i in range(num_levels):
            anchors = self.grid_anchors(featmap_sizes[i], self.base_sizes[i])
            multi_level_anchors += (Tensor(anchors.astype(np.float32)),)

        return multi_level_anchors

    @staticmethod
    def check_anchors(anchor_list, img_metas):
        """Check anchors."""
        multi_level_flags = ()
        for anchors in anchor_list:
            res = P.Cast()(P.CheckValid()(anchors, P.Squeeze()(img_metas)), mstype.bool_)
            multi_level_flags = multi_level_flags + (res,)
        return multi_level_flags


@ClassFactory.register(ModuleType.ANCHOR_GENERATOR)
class YoloAnchorGenerator(AnchorGenerator):
    """Yolo anchor boxes generator."""

    def __init__(self, anchor_scales, anchor_mask):
        """Constructor for YoloAnchorGenerator."""
        AnchorGenerator.__init__(self, [], [], [])
        self.scales = anchor_scales
        self.anchor_mask = anchor_mask

    # pylint: disable=W0221
    def get_anchors(self, feat_idxs):
        """Get anchors according to feature id"""
        anchors = []
        for i in feat_idxs:
            anchors.append(self.scales[i])

        return Tensor(anchors, ms.float32)


def meshgrid(x, y):
    """Generate grid."""
    xx = np.repeat(x.reshape(1, len(x)), len(y), axis=0).reshape(-1)
    yy = np.repeat(y, len(x))
    return xx, yy
