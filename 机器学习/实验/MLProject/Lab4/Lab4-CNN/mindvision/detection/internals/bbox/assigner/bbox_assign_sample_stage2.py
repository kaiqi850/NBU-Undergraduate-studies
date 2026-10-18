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
"""FasterRcnn tpositive and negative sample screening for Rcnn."""

import mindspore.common.dtype as mstype
import mindspore.nn as nn
import numpy as np
from mindspore.common.tensor import Tensor
from mindspore.ops import operations as P


class BboxAssignSampleForRcnn(nn.Cell):
    """
    Bbox assigner and sampler definition.

    Args:
        assigner (dict): Assigner.
        sampler (dict): Sampler.
        num_gts (int): Ground truth Numbers.
        batch_size (int): Batch size.
        num_bboxes (int): The anchor nums.
        add_gt_as_proposals (bool): Add gt bboxes as proposals flag.

    Returns:
        total_bboxes: bbox location, (batch_size, num_bboxes, 4).
        total_deltas: bbox deltas, (batch_size, num_bboxes, 1).
        total_labels: label for every bboxes, (batch_size, num_bboxes, 1).
        total_mask: label weight for every bboxes, (batch_size, num_bboxes, 1).

    Examples:
        BboxAssignSampleForRcnn(assigner, sampler, 128, 2, 1024, True).
    """

    def __init__(self, assigner, sampler, num_gts, batch_size, img_height, img_width, mask_shape, \
                 num_bboxes, add_gt_as_proposals):
        super(BboxAssignSampleForRcnn, self).__init__()
        self.dtype = np.float32
        self.ms_type = mstype.float32
        self.batch_size = batch_size
        self.img_height = img_height
        self.img_width = img_width
        self.mask_shape = (mask_shape[0], mask_shape[1])
        self.neg_iou_thr = assigner.neg_iou_thr
        self.pos_iou_thr = assigner.pos_iou_thr
        self.min_pos_iou = assigner.min_pos_iou
        self.num_gts = num_gts
        self.num_bboxes = num_bboxes
        self.num_expected_pos = sampler.num_expected_pos
        self.num_expected_neg = sampler.num_expected_neg
        self.num_expected_total = sampler.num_expected_total

        self.add_gt_as_proposals = add_gt_as_proposals
        self.label_inds = Tensor(np.arange(1, self.num_gts + 1).astype(np.int32))
        self.add_gt_as_proposals_valid = Tensor(
            np.full(self.num_gts, self.add_gt_as_proposals, dtype=np.int32)
        )

        self.concat = P.Concat(axis=0)
        self.max_gt = P.ArgMaxWithValue(axis=0)
        self.max_anchor = P.ArgMaxWithValue(axis=1)
        self.sum_inds = P.ReduceSum()
        self.iou = P.IOU()
        self.greaterequal = P.GreaterEqual()
        self.greater = P.Greater()
        self.select = P.Select()
        self.gather_nd = P.GatherNd()
        self.squeeze = P.Squeeze()
        self.cast = P.Cast()
        self.logicaland = P.LogicalAnd()
        self.less = P.Less()
        self.random_choice_with_mask_pos = P.RandomChoiceWithMask(self.num_expected_pos)
        self.random_choice_with_mask_neg = P.RandomChoiceWithMask(self.num_expected_neg)
        self.reshape = P.Reshape()
        self.equal = P.Equal()
        self.bounding_box_encode = P.BoundingBoxEncode(means=(0.0, 0.0, 0.0, 0.0), stds=(0.1, 0.1, 0.2, 0.2))
        self.concat_axis1 = P.Concat(axis=1)
        self.logicalnot = P.LogicalNot()
        self.tile = P.Tile()

        # Check
        self.check_gt_one = Tensor(np.full((self.num_gts, 4), -1, dtype=self.dtype))
        self.check_anchor_two = Tensor(np.full((self.num_bboxes, 4), -2, dtype=self.dtype))

        # Init tensor
        self.assigned_gt_inds = Tensor(np.full(num_bboxes, -1, dtype=np.int32))
        self.assigned_gt_zeros = Tensor(np.array(np.zeros(num_bboxes), dtype=np.int32))
        self.assigned_gt_ones = Tensor(np.array(np.ones(num_bboxes), dtype=np.int32))
        self.assigned_gt_ignores = Tensor(np.full(num_bboxes, -1, dtype=np.int32))
        self.assigned_pos_ones = Tensor(np.array(np.ones(self.num_expected_pos), dtype=np.int32))

        self.gt_ignores = Tensor(np.full(self.num_gts, -1, dtype=np.int32))
        self.range_pos_size = Tensor(np.arange(self.num_expected_pos).astype(self.dtype))
        self.check_neg_mask = Tensor(
            np.array(np.ones(self.num_expected_neg - self.num_expected_pos), dtype=np.bool)
        )
        self.bboxs_neg_mask = Tensor(np.zeros((self.num_expected_neg, 4), dtype=self.dtype))
        self.labels_neg_mask = Tensor(np.array(np.zeros(self.num_expected_neg), dtype=np.uint8))

        self.reshape_shape_pos = (self.num_expected_pos, 1)
        self.reshape_shape_neg = (self.num_expected_neg, 1)

        self.scalar_zero = Tensor(0.0, dtype=self.ms_type)
        self.scalar_neg_iou_thr = Tensor(self.neg_iou_thr, dtype=self.ms_type)
        self.scalar_pos_iou_thr = Tensor(self.pos_iou_thr, dtype=self.ms_type)
        self.scalar_min_pos_iou = Tensor(self.min_pos_iou, dtype=self.ms_type)

        self.expand_dims = P.ExpandDims()
        self.split = P.Split(axis=1, output_num=4)
        self.concat_last_axis = P.Concat(axis=-1)
        self.round = P.Round()
        self.image_h_w = Tensor([self.img_height, self.img_width, \
                                 self.img_height, self.img_width], dtype=mstype.float32)
        self.range = nn.Range(start=0, limit=self.num_gts)
        self.crop_and_resize = P.CropAndResize(method="bilinear_v2")
        self.squeeze_mask_last = P.Squeeze(axis=-1)

    def construct(self, gt_bboxes_i, gt_labels_i, valid_mask, bboxes, gt_valids, gt_masks_i=None):
        """construct of BboxAssignSampleForRcnn, return total bbox, delta, labels and mask."""
        gt_bboxes_i = self.select(
            self.cast(self.tile(self.reshape(self.cast(gt_valids, mstype.int32),
                                             (self.num_gts, 1)), (1, 4)), mstype.bool_),
            gt_bboxes_i, self.check_gt_one
        )

        bboxes = self.select(
            self.cast(self.tile(self.reshape(self.cast(valid_mask, mstype.int32),
                                             (self.num_bboxes, 1)), (1, 4)), mstype.bool_),
            bboxes, self.check_anchor_two
        )

        overlaps = self.iou(bboxes, gt_bboxes_i)

        max_overlaps_w_gt_index, max_overlaps_w_gt = self.max_gt(overlaps)
        _, max_overlaps_w_ac = self.max_anchor(overlaps)

        neg_sample_iou_mask = self.logicaland(
            self.greaterequal(max_overlaps_w_gt, self.scalar_zero),
            self.less(max_overlaps_w_gt, self.scalar_neg_iou_thr)
        )

        assigned_gt_inds2 = self.select(
            neg_sample_iou_mask, self.assigned_gt_zeros, self.assigned_gt_inds
        )

        pos_sample_iou_mask = self.greaterequal(max_overlaps_w_gt, self.scalar_pos_iou_thr)
        assigned_gt_inds3 = self.select(
            pos_sample_iou_mask,
            max_overlaps_w_gt_index + self.assigned_gt_ones,
            assigned_gt_inds2
        )

        for j in range(self.num_gts):
            max_overlaps_w_ac_j = max_overlaps_w_ac[j:j + 1:1]
            overlaps_w_ac_j = overlaps[j:j + 1:1, ::]
            temp1 = self.greaterequal(max_overlaps_w_ac_j, self.scalar_min_pos_iou)
            temp2 = self.squeeze(self.equal(overlaps_w_ac_j, max_overlaps_w_ac_j))
            pos_mask_j = self.logicaland(temp1, temp2)
            assigned_gt_inds3 = self.select(
                pos_mask_j,
                (j + 1) * self.assigned_gt_ones,
                assigned_gt_inds3
            )

        assigned_gt_inds5 = self.select(
            valid_mask,
            assigned_gt_inds3,
            self.assigned_gt_ignores
        )

        bboxes = self.concat((gt_bboxes_i, bboxes))
        label_inds_valid = self.select(gt_valids, self.label_inds, self.gt_ignores)
        label_inds_valid = label_inds_valid * self.add_gt_as_proposals_valid
        assigned_gt_inds5 = self.concat((label_inds_valid, assigned_gt_inds5))

        # Get pos index
        pos_index, valid_pos_index = self.random_choice_with_mask_pos(
            self.greater(assigned_gt_inds5, 0)
        )

        pos_check_valid = self.cast(self.greater(assigned_gt_inds5, 0), self.ms_type)
        pos_check_valid = self.sum_inds(pos_check_valid, -1)
        valid_pos_index = self.less(self.range_pos_size, pos_check_valid)
        pos_index = pos_index * self.reshape(
            self.cast(valid_pos_index, mstype.int32),
            (self.num_expected_pos, 1)
        )

        num_pos = self.sum_inds(self.cast(self.logicalnot(valid_pos_index), self.ms_type), -1)
        valid_pos_index = self.cast(valid_pos_index, mstype.int32)
        pos_index = self.reshape(pos_index, self.reshape_shape_pos)
        valid_pos_index = self.reshape(valid_pos_index, self.reshape_shape_pos)
        pos_index = pos_index * valid_pos_index

        pos_assigned_gt_index = self.gather_nd(assigned_gt_inds5, pos_index) - self.assigned_pos_ones
        pos_assigned_gt_index = self.reshape(pos_assigned_gt_index, self.reshape_shape_pos)
        pos_assigned_gt_index = pos_assigned_gt_index * valid_pos_index

        pos_gt_labels = self.gather_nd(gt_labels_i, pos_assigned_gt_index)

        # Get neg index
        neg_index, valid_neg_index = self.random_choice_with_mask_neg(
            self.equal(assigned_gt_inds5, 0)
        )

        unvalid_pos_index = self.less(self.range_pos_size, num_pos)
        valid_neg_index = self.logicaland(
            self.concat((self.check_neg_mask, unvalid_pos_index)),
            valid_neg_index
        )
        neg_index = self.reshape(neg_index, self.reshape_shape_neg)

        valid_neg_index = self.cast(valid_neg_index, mstype.int32)
        valid_neg_index = self.reshape(valid_neg_index, self.reshape_shape_neg)
        neg_index = neg_index * valid_neg_index

        pos_bboxes_ = self.gather_nd(bboxes, pos_index)

        neg_bboxes_ = self.gather_nd(bboxes, neg_index)
        pos_assigned_gt_index = self.reshape(pos_assigned_gt_index, self.reshape_shape_pos)
        pos_gt_bboxes_ = self.gather_nd(gt_bboxes_i, pos_assigned_gt_index)
        pos_bbox_targets_ = self.bounding_box_encode(pos_bboxes_, pos_gt_bboxes_)

        total_bboxes = self.concat((pos_bboxes_, neg_bboxes_))
        total_deltas = self.concat((pos_bbox_targets_, self.bboxs_neg_mask))
        total_labels = self.concat((pos_gt_labels, self.labels_neg_mask))

        valid_pos_index = self.reshape(valid_pos_index, self.reshape_shape_pos)
        valid_neg_index = self.reshape(valid_neg_index, self.reshape_shape_neg)
        total_mask = self.concat((valid_pos_index, valid_neg_index))

        # assign positive ROIs to gt masks
        # Pick the right front and background mask for each ROI
        if gt_masks_i is not None:
            roi_pos_masks_fb = self.gather_nd(gt_masks_i, pos_assigned_gt_index)
            pos_masks_fb = self.expand_dims(self.cast(roi_pos_masks_fb, mstype.float32), -1)
            # compute mask targets
            x1, y1, x2, y2 = self.split(pos_bboxes_)

            boxes = self.cast(self.concat_last_axis((y1, x1, y2, x2)) / self.image_h_w, mstype.float32)

            pos_masks_fb = self.crop_and_resize(pos_masks_fb, boxes, self.range(), self.mask_shape)

            # Remove the extra dimension from masks.
            pos_masks_fb = self.round(self.squeeze_mask_last(pos_masks_fb))

            pos_masks_fb = self.cast(pos_masks_fb, mstype.float32)

            return total_bboxes, total_deltas, total_labels, total_mask, \
                   pos_bboxes_, pos_masks_fb, pos_gt_labels, valid_pos_index

        return total_bboxes, total_deltas, total_labels, total_mask, pos_bboxes_
