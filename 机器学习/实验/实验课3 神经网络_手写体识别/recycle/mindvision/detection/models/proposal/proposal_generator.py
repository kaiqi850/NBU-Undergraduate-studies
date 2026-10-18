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
"""FasterRcnn proposal generator."""

import mindspore.common.dtype as mstype
import mindspore.nn as nn
import numpy as np
from mindspore import Tensor
from mindspore.ops import operations as P


class Proposal(nn.Cell):
    """Proposal subnet.

    Args:
        config (dict): Config.
        batch_size (int): Batchsize.
        num_classes (int) - Class number.
        use_sigmoid_cls (bool) - Select sigmoid or softmax function.
        target_means (tuple) - Means for encode function. Default: (.0, .0, .0, .0).
        target_stds (tuple) - Stds for encode function. Default: (1.0, 1.0, 1.0, 1.0).

    Returns:
        Tuple, tuple of output tensor,(proposal, mask).

    Examples:
        Proposal(config = config, batch_size = 1, num_classes = 81, use_sigmoid_cls = True, \
                 target_means=(.0, .0, .0, .0), target_stds=(1.0, 1.0, 1.0, 1.0))
    """

    def __init__(self,
                 propsal_config,
                 batch_size,
                 feature_shapes,
                 training,
                 target_means=(.0, .0, .0, .0),
                 target_stds=(1.0, 1.0, 1.0, 1.0)
                 ):
        super(Proposal, self).__init__()
        cfg = propsal_config
        self.batch_size = batch_size
        self.target_means = target_means
        self.target_stds = target_stds
        self.use_sigmoid_cls = cfg.use_sigmoid_cls
        if self.use_sigmoid_cls:
            self.activation = P.Sigmoid()
            self.reshape_shape = (-1, 1)
        else:
            self.activation = P.Softmax(axis=1)
            self.reshape_shape = (-1, 2)
        self.num_pre = cfg.nms_pre
        self.min_box_size = cfg.min_bbox_size
        self.nms_thr = cfg.nms_thr
        self.nms_post = cfg.nms_post
        self.max_num = cfg.max_num
        self.num_levels = cfg.fpn_num_outs

        # Op Define
        self.squeeze = P.Squeeze()
        self.reshape = P.Reshape()
        self.cast = P.Cast()
        self.feature_shapes = feature_shapes
        self.transpose_shape = (1, 2, 0)
        self.decode = P.BoundingBoxDecode(
            max_shape=(cfg.img_height, cfg.img_width),
            means=self.target_means,
            stds=self.target_stds
        )
        self.nms = P.NMSWithMask(self.nms_thr)
        self.concat_axis0 = P.Concat(axis=0)
        self.concat_axis1 = P.Concat(axis=1)
        self.split = P.Split(axis=1, output_num=5)
        self.min = P.Minimum()
        self.gather_nd = P.GatherNd()
        self.slice = P.Slice()
        self.select = P.Select()
        self.greater = P.Greater()
        self.transpose = P.Transpose()
        self.tile = P.Tile()
        self.set_train_local(propsal_config, training)
        self.dtype = np.float32
        self.ms_type = mstype.float32
        self.multi_10 = Tensor(10.0, self.ms_type)

    def set_train_local(self, config, training=True):
        """Set training flag."""
        self.training_local = training
        cfg = config
        self.topk_stage1 = ()
        self.topk_shape = ()
        total_max_topk_input = 0
        if not self.training_local:
            self.num_pre = cfg.nms_pre
            self.min_box_size = cfg.min_bbox_size
            self.nms_thr = cfg.nms_thr
            self.nms_post = cfg.nms_post
            self.max_num = cfg.max_num
        for shp in self.feature_shapes:
            k_num = min(self.num_pre, (shp[0] * shp[1] * 3))
            total_max_topk_input += k_num
            self.topk_stage1 += (k_num,)
            self.topk_shape += ((k_num, 1),)
        self.topk_v2 = P.TopK(sorted=True)
        self.topk_shape_stage2 = (self.max_num, 1)
        self.min_float_num = -65500.0
        self.topk_mask = Tensor(self.min_float_num * np.ones(total_max_topk_input, np.float32))

    def construct(self, rpn_cls_score_total, rpn_bbox_pred_total, anchor_list):
        """Construct of proposal."""
        proposals_tuple = ()
        masks_tuple = ()
        for img_id in range(self.batch_size):
            cls_score_list = ()
            bbox_pred_list = ()
            for i in range(self.num_levels):
                rpn_cls_score_i = \
                    self.squeeze(rpn_cls_score_total[i][img_id:img_id + 1:1, ::, ::, ::])
                rpn_bbox_pred_i = \
                    self.squeeze(rpn_bbox_pred_total[i][img_id:img_id + 1:1, ::, ::, ::])

                cls_score_list = cls_score_list + (rpn_cls_score_i,)
                bbox_pred_list = bbox_pred_list + (rpn_bbox_pred_i,)

            proposals, masks = self.get_bboxes_single(cls_score_list, bbox_pred_list, anchor_list)
            proposals_tuple += (proposals,)
            masks_tuple += (masks,)

        return proposals_tuple, masks_tuple

    def get_bboxes_single(self, cls_scores, bbox_preds, mlvl_anchors):
        """Get proposal bounding box level-wise."""
        mlvl_proposals = ()
        mlvl_mask = ()
        for idx in range(self.num_levels):
            rpn_cls_score = self.transpose(cls_scores[idx], self.transpose_shape)
            rpn_bbox_pred = self.transpose(bbox_preds[idx], self.transpose_shape)

            anchors = mlvl_anchors[idx]
            rpn_cls_score = self.reshape(rpn_cls_score, self.reshape_shape)
            rpn_cls_score = self.activation(rpn_cls_score)

            rpn_cls_score_process = \
                self.cast(self.squeeze(rpn_cls_score[::, 0::]), self.ms_type)
            rpn_bbox_pred_process = \
                self.cast(self.reshape(rpn_bbox_pred, (-1, 4)), self.ms_type)
            scores_sorted, topk_inds = \
                self.topk_v2(rpn_cls_score_process, self.topk_stage1[idx])

            topk_inds = self.reshape(topk_inds, self.topk_shape[idx])
            bboxes_sorted = self.gather_nd(rpn_bbox_pred_process, topk_inds)
            anchors_sorted = self.cast(self.gather_nd(anchors, topk_inds), self.ms_type)
            proposals_decode = self.decode(anchors_sorted, bboxes_sorted)

            proposals_decode = \
                self.concat_axis1((proposals_decode, self.reshape(scores_sorted, self.topk_shape[idx])))

            proposals, _, mask_valid = self.nms(proposals_decode)
            mlvl_proposals = mlvl_proposals + (proposals,)
            mlvl_mask = mlvl_mask + (mask_valid,)

        proposals = self.concat_axis0(mlvl_proposals)
        masks = self.concat_axis0(mlvl_mask)

        _, _, _, _, scores = self.split(proposals)
        scores = self.squeeze(scores)

        topk_mask = self.cast(self.topk_mask, self.ms_type)
        scores_using = self.select(masks, scores, topk_mask)

        _, topk_inds = self.topk_v2(scores_using, self.max_num)
        topk_inds = self.reshape(topk_inds, self.topk_shape_stage2)

        proposals = self.gather_nd(proposals, topk_inds)
        masks = self.gather_nd(masks, topk_inds)

        return proposals, masks
