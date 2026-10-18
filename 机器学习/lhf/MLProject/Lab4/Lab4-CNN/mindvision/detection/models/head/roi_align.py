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
"""FasterRcnn ROIAlign module."""

import mindspore.common.dtype as mstype
import mindspore.nn as nn
import numpy as np
from mindspore.common.tensor import Tensor
from mindspore.nn import layer as L
from mindspore.ops import composite as C
from mindspore.ops import operations as P


class ROIAlign(nn.Cell):
    """
    Extract RoI features from multiple feature map.

    Args:
        out_size_h (int) - RoI height.
        out_size_w (int) - RoI width.
        spatial_scale (int) - RoI spatial scale.
        sample_num (int) - RoI sample number.
    """

    def __init__(self,
                 out_size_h,
                 out_size_w,
                 spatial_scale,
                 sample_num=0):
        super(ROIAlign, self).__init__()

        self.out_size = (out_size_h, out_size_w)
        self.spatial_scale = float(spatial_scale)
        self.sample_num = int(sample_num)
        self.align_op = P.ROIAlign(self.out_size[0], self.out_size[1],
                                   self.spatial_scale, self.sample_num)

    def construct(self, features, rois):
        return self.align_op(features, rois)

    def __repr__(self):
        format_str = self.__class__.__name__
        format_str += '(out_size={}, spatial_scale={}, sample_num={}'.format(
            self.out_size, self.spatial_scale, self.sample_num)
        return format_str


class SingleRoIExtractor(nn.Cell):
    """
    Extract RoI features from a single level feature map.

    If there are multiple input feature levels, each RoI is mapped to a level
    according to its scale.

    Args:
        config (dict): Config
        roi_layer (dict): Specify RoI layer type and arguments.
        out_channels (int): Output channels of RoI layers.
        featmap_strides (int): Strides of input feature maps.
        batch_size (int): Batchsize.
        finest_scale (int): Scale threshold of mapping to level 0.
    """

    def __init__(self,
                 config,
                 finest_scale=56, with_mask=False):
        super(SingleRoIExtractor, self).__init__()
        self.with_mask = with_mask
        self.out_channels = config.out_channels
        self.featmap_strides = config.featmap_strides
        self.num_levels = len(self.featmap_strides)
        self.out_size = config.roi_layer['mask_out_size'] if self.with_mask else config.roi_layer['output_size']
        self.sample_num = config.roi_layer['sample_num']
        self.roi_layers = self.build_roi_layers(self.featmap_strides)
        self.roi_layers = L.CellList(self.roi_layers)

        self.ones = None
        self.zeros = None
        self.twos = None
        self.res_ = None
        self.batch_size = 0
        self.finest_scale = 0
        self.epslion = 0
        self.max_levels = 0

        self.sqrt = P.Sqrt()
        self.log = P.Log()
        self.finest_scale_ = finest_scale
        self.clamp = C.clip_by_value

        self.cast = P.Cast()
        self.equal = P.Equal()
        self.select = P.Select()

        mode_16_ = False
        self.dtype = np.float16 if mode_16_ else np.float32
        self.ms_dtype = mstype.float16 if mode_16_ else mstype.float32

    def set_train_local(self, img_batch_size, train_cfg, test_cfg, training=True):
        """Set training flag."""
        # Init tensor
        train_total_num = train_cfg.rcnn.sampler.num_expected_pos if self.with_mask \
            else (train_cfg.rcnn.sampler.num_expected_pos + train_cfg.rcnn.sampler.num_expected_neg)
        test_total_num = test_cfg.proposal.max_num
        self.batch_size = img_batch_size * (train_total_num if training else test_total_num)
        self.ones = Tensor(np.array(np.ones((self.batch_size, 1)), dtype=self.dtype))
        finest_scale = np.array(np.ones((self.batch_size, 1)), dtype=self.dtype) * self.finest_scale_
        self.finest_scale = Tensor(finest_scale)
        self.epslion = Tensor(np.array(np.ones((self.batch_size, 1)), dtype=self.dtype) * self.dtype(1e-6))
        self.zeros = Tensor(np.array(np.zeros((self.batch_size, 1)), dtype=np.int32))
        self.max_levels = Tensor(np.array(np.ones((self.batch_size, 1)), dtype=np.int32) * (self.num_levels - 1))
        self.twos = Tensor(np.array(np.ones((self.batch_size, 1)), dtype=self.dtype) * 2)
        self.res_ = Tensor(np.array(np.zeros((self.batch_size, self.out_channels,
                                              self.out_size, self.out_size)), dtype=self.dtype))

    def num_inputs(self):
        """Number inputs."""
        return len(self.featmap_strides)

    # def init_weights(self):
    #     """ROI initialize weights."""
    #     pass

    def log2(self, value):
        """Get log2(value)."""
        return self.log(value) / self.log(self.twos)

    def build_roi_layers(self, featmap_strides):
        """Build roi layers."""
        roi_layers = []
        for s in featmap_strides:
            layer_cls = ROIAlign(self.out_size, self.out_size,
                                 spatial_scale=1 / s,
                                 sample_num=self.sample_num)
            roi_layers.append(layer_cls)
        return roi_layers

    def _c_map_roi_levels(self, rois):
        """Map rois to corresponding feature levels by scales.

        - scale < finest_scale * 2: level 0
        - finest_scale * 2 <= scale < finest_scale * 4: level 1
        - finest_scale * 4 <= scale < finest_scale * 8: level 2
        - scale >= finest_scale * 8: level 3

        Args:
            rois (Tensor): Input RoIs, shape (k, 5).
            num_levels (int): Total level number.

        Returns:
            Tensor: Level index (0-based) of each RoI, shape (k, )
        """
        scale = \
            self.sqrt(rois[::, 3:4:1] - rois[::, 1:2:1] + self.ones) * \
            self.sqrt(rois[::, 4:5:1] - rois[::, 2:3:1] + self.ones)

        target_lvls = self.log2(scale / self.finest_scale + self.epslion)
        target_lvls = P.Floor()(target_lvls)
        target_lvls = self.cast(target_lvls, mstype.int32)
        target_lvls = self.clamp(target_lvls, self.zeros, self.max_levels)

        return target_lvls

    def construct(self, rois, feat1, feat2, feat3, feat4):
        """Construct of roi_align."""
        feats = (feat1, feat2, feat3, feat4)
        res = self.res_
        target_lvls = self._c_map_roi_levels(rois)
        for i in range(self.num_levels):
            mask = self.equal(target_lvls, P.ScalarToArray()(i))
            mask = P.Reshape()(mask, (-1, 1, 1, 1))
            roi_feats_t = self.roi_layers[i](feats[i], rois)
            mask = self.cast(P.Tile()(self.cast(mask, mstype.int32),
                                      (1, 256, self.out_size, self.out_size)),
                             mstype.bool_)
            res = self.select(mask, roi_feats_t, res)

        return res
