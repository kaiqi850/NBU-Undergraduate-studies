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
"""RPN for fasterRCNN"""
import numpy as np

import mindspore.nn as nn
import mindspore.common.dtype as mstype
from mindspore import context, Tensor
from mindspore.ops import functional as F
from mindspore.ops import operations as P

from mindvision.detection.internals.bbox.assigner.bbox_assign_sample_stage2 import BboxAssignSampleForRcnn
from mindvision.detection.models.head.roi_align import SingleRoIExtractor
from mindvision.detection.models.meta_arch.rcnn import Rcnn
from mindvision.detection.models.meta_arch.rcnn_mask import RcnnMask
from mindvision.engine.class_factory import ClassFactory, ModuleType


@ClassFactory.register(ModuleType.HEAD)
class StandardRoIHead(nn.Cell):
    """ROI proposal network.

    Args:
        config (dict) - Config.
        batch_size (int) - Batchsize.
        in_channels (int) - Input channels of shared convolution.
        feat_channels (int) - Output channels of shared convolution.
        num_anchors (int) - The anchor number.
        cls_out_channels (int) - Output channels of classification convolution.

    Returns:
        Tuple, tuple of output tensor.

    Examples:
        RPN(config=config, batch_size=2, in_channels=256, feat_channels=1024,
            num_anchors=3, cls_out_channels=512)
    """

    def __init__(self, config, bbox_roi_extractor, bbox_head, train_cfg, test_cfg):
        super(StandardRoIHead, self).__init__()
        self.config = config
        self.with_mask = config.with_mask
        self.num_classes = config.num_classes
        self.concat = P.Concat(axis=0)
        self.concat_1 = P.Concat(axis=1)
        self.batch_size = config.batch_size

        self.target_means = tuple(bbox_head.bbox_coder.target_means)
        self.target_stds = tuple(bbox_head.bbox_coder.target_stds)
        self.reshape = P.Reshape()
        self.select = P.Select()
        self.greater = P.Greater()
        self.dtype = np.float32
        self.cast = P.Cast()
        self.squeeze = P.Squeeze()
        self.ms_type = mstype.float32
        # Improve speed
        self.concat_start = min(config.num_classes - 2, 55)
        self.concat_end = (config.num_classes - 1)
        self.decode = P.BoundingBoxDecode(max_shape=(config.img_height, config.img_width),
                                          means=self.target_means,
                                          stds=self.target_stds)
        self.bbox_assigner_sampler_for_rcnn = BboxAssignSampleForRcnn(train_cfg.rcnn.assigner,
                                                                      train_cfg.rcnn.sampler,
                                                                      config.num_gts, config.batch_size,
                                                                      config.img_height,
                                                                      config.img_width,
                                                                      config.mask_shape,
                                                                      train_cfg.rcnn.num_bboxes_stage2, True)
        self.rcnn = Rcnn(train_cfg.rcnn,
                         bbox_head.in_channels * bbox_roi_extractor.roi_layer.output_size
                         * bbox_roi_extractor.roi_layer.output_size,
                         config.num_classes,
                         (train_cfg.rcnn.sampler.num_expected_pos + train_cfg.rcnn.sampler.num_expected_neg)
                         * config.batch_size)

        self._roi_init(bbox_roi_extractor, config.batch_size, config.test_batch_size, train_cfg, test_cfg)
        self._init_tensor(config, train_cfg, test_cfg)
        # Test mode
        self.test_mode_init(config, test_cfg)
        self.device_type = "Ascend" if context.get_context("device_target") == "Ascend" else "Others"

        if self.with_mask:
            self.rcnn_mask = RcnnMask(train_cfg.rcnn, self.batch_size, self.num_classes)

    def test_mode_init(self, config, test_cfg):
        """Roi test init."""
        self.rpn_max_num = test_cfg.proposal.max_num
        self.test_batch_size = config.test_batch_size
        self.split = P.Split(axis=0, output_num=config.test_batch_size)
        self.split_shape = P.Split(axis=0, output_num=4)
        self.split_scores = P.Split(axis=1, output_num=config.num_classes)
        self.split_cls = P.Split(axis=0, output_num=config.num_classes - 1)
        self.tile = P.Tile()
        self.gather = P.GatherNd()

        self.zeros_for_nms = Tensor(np.zeros((self.rpn_max_num, 3)).astype(self.dtype))
        self.ones_mask = np.ones((self.rpn_max_num, 1)).astype(np.bool)
        self.zeros_mask = np.zeros((self.rpn_max_num, 1)).astype(np.bool)
        self.bbox_mask = Tensor(np.concatenate((self.ones_mask, self.zeros_mask,
                                                self.ones_mask, self.zeros_mask), axis=1))
        self.nms_pad_mask = Tensor(np.concatenate((self.ones_mask, self.ones_mask,
                                                   self.ones_mask, self.ones_mask, self.zeros_mask), axis=1))

        self.test_score_thresh = Tensor(np.ones((self.rpn_max_num, 1)).astype(self.dtype) * test_cfg.rcnn.score_thr)
        self.test_score_zeros = Tensor(np.ones((self.rpn_max_num, 1)).astype(self.dtype) * 0)
        self.test_box_zeros = Tensor(np.ones((self.rpn_max_num, 4)).astype(self.dtype) * -1)
        self.test_max_per_img = test_cfg.rcnn.max_per_img
        self.nms_test = P.NMSWithMask(test_cfg.rcnn.nms.iou_threshold)
        self.softmax = P.Softmax(axis=1)
        self.logicand = P.LogicalAnd()
        self.oneslike = P.OnesLike()
        self.test_topk = P.TopK(sorted=True)
        self.test_num_proposal = self.test_batch_size * self.rpn_max_num

        if self.with_mask:
            self.split_fb_mask = P.Split(axis=1, output_num=self.num_classes)
            self.argmax_with_value = P.ArgMaxWithValue(axis=1)
            self.on_value = Tensor(1.0, mstype.float32)
            self.off_value = Tensor(0.0, mstype.float32)
            self.onehot = P.OneHot()
            self.reducesum = P.ReduceSum()
            self.sigmoid = P.Sigmoid()
            self.expand_dims = P.ExpandDims()
            self.test_mask_fb_zeros = Tensor(np.zeros((self.rpn_max_num, 28, 28)).astype(np.float32))
            self.value = Tensor(1.0, mstype.float32)

    def _init_tensor(self, config, train_cfg, test_cfg):
        """Roi align tensor init"""
        roi_align_index = [np.array(np.ones((train_cfg.rcnn.sampler.num_expected_pos
                                             + train_cfg.rcnn.sampler.num_expected_neg, 1)) * i,
                                    dtype=self.dtype) for i in range(config.batch_size)]

        roi_align_index_test = [np.array(np.ones((test_cfg.proposal.max_num, 1)) * i, dtype=self.dtype)
                                for i in range(config.test_batch_size)]

        self.roi_align_index_tensor = Tensor(np.concatenate(roi_align_index))
        self.roi_align_index_test_tensor = Tensor(np.concatenate(roi_align_index_test))

        roi_align_index_pos = [np.array(np.ones((config.num_gts, 1)) * i,
                                        dtype=np.float32) for i in range(config.batch_size)]
        self.roi_align_index_tensor_pos = Tensor(np.concatenate(roi_align_index_pos))

    def _roi_init(self, config, batch_size, test_batch_size, train_cfg, test_cfg):
        """Roi align init"""
        self.roi_align = SingleRoIExtractor(config)
        self.roi_align.set_train_local(batch_size, train_cfg, test_cfg, True)
        self.roi_align_test = SingleRoIExtractor(config)
        self.roi_align_test.set_train_local(test_batch_size, train_cfg, test_cfg, False)

        if self.with_mask:
            self.roi_align_mask = SingleRoIExtractor(config, with_mask=True)
            self.roi_align_mask.set_train_local(batch_size, train_cfg, test_cfg, True)
            self.roi_align_mask_test = SingleRoIExtractor(config, with_mask=True)
            self.roi_align_mask_test.set_train_local(test_batch_size, train_cfg, test_cfg, False)

    def get_det_bboxes(self, cls_logits, reg_logits, mask_logits, rois, img_metas, mask_fb_pred_all=None):
        """Get the actual detection box."""
        scores = self.softmax(cls_logits)

        boxes_all = ()
        for i in range(self.num_classes):
            k = i * 4
            reg_logits_i = self.squeeze(reg_logits[::, k:k + 4:1])
            out_boxes_i = self.decode(rois, reg_logits_i)
            boxes_all += (out_boxes_i,)

        img_metas_all = self.split(img_metas)
        scores_all = self.split(scores)
        mask_all = self.split(self.cast(mask_logits, mstype.int32))

        boxes_all_with_batchsize = ()
        for i in range(self.test_batch_size):
            scale = self.split_shape(self.squeeze(img_metas_all[i]))
            scale_h = scale[2]
            scale_w = scale[3]
            boxes_tuple = ()
            for j in range(self.num_classes):
                boxes_tmp = self.split(boxes_all[j])
                out_boxes_h = boxes_tmp[i] / scale_h
                out_boxes_w = boxes_tmp[i] / scale_w
                boxes_tuple += (self.select(self.bbox_mask, out_boxes_w, out_boxes_h),)
            boxes_all_with_batchsize += (boxes_tuple,)

        if self.with_mask:
            mask_fb_logits = self.sigmoid(mask_fb_pred_all)
            mask_fb_all = self.split(mask_fb_logits)
            mask_output = self._multiclass_nms(boxes_all_with_batchsize, scores_all, mask_all, mask_fb_all)
            return mask_output

        output = self._multiclass_nms(boxes_all_with_batchsize, scores_all, mask_all)
        return output

    def _multiclass_nms(self, boxes_all, scores_all, mask_all, mask_fb_all=None):
        """Multiscale postprocessing."""
        all_bboxes = ()
        all_labels = ()
        all_masks = ()
        all_masks_fb = ()

        for i in range(self.test_batch_size):
            bboxes = boxes_all[i]
            scores = scores_all[i]
            masks = self.cast(mask_all[i], mstype.bool_)

            res_boxes_tuple = ()
            res_labels_tuple = ()
            res_masks_tuple = ()
            res_masks_fb_tuple = ()

            for j in range(self.num_classes - 1):
                k = j + 1
                cls_scores_ = scores[::, k:k + 1:1]
                bboxes_ = self.squeeze(bboxes[k])
                mask_o_ = self.reshape(masks, (self.rpn_max_num, 1))

                cls_mask = self.greater(cls_scores_, self.test_score_thresh)
                mask_ = self.logicand(mask_o_, cls_mask)

                reg_mask_ = self.cast(self.tile(self.cast(mask_, mstype.int32), (1, 4)), mstype.bool_)

                bboxes_ = self.select(reg_mask_, bboxes_, self.test_box_zeros)
                cls_scores_ = self.select(mask_, cls_scores_, self.test_score_zeros)
                cls_scores__ = self.squeeze(cls_scores_)
                scores_sorted, topk_inds = self.test_topk(cls_scores__, self.rpn_max_num)
                topk_inds = self.reshape(topk_inds, (self.rpn_max_num, 1))
                scores_sorted = self.reshape(scores_sorted, (self.rpn_max_num, 1))
                bboxes_sorted_ = self.gather(bboxes_, topk_inds)
                mask_sorted_ = self.gather(mask_, topk_inds)

                scores_sorted = self.tile(scores_sorted, (1, 4))
                cls_dets = self.concat_1((bboxes_sorted_, scores_sorted))
                cls_dets = P.Slice()(cls_dets, (0, 0), (self.rpn_max_num, 5))

                cls_dets, index_, mask_nms_ = self.nms_test(cls_dets)
                index_ = self.reshape(index_, (self.rpn_max_num, 1))
                mask_nms_ = self.reshape(mask_nms_, (self.rpn_max_num, 1))

                mask_n_ = self.gather(mask_sorted_, index_)

                mask_n_ = self.logicand(mask_n_, mask_nms_)
                cls_labels = self.oneslike(index_) * j
                res_boxes_tuple += (cls_dets,)
                res_labels_tuple += (cls_labels,)
                res_masks_tuple += (mask_n_,)

                if self.with_mask:
                    masks_fb = mask_fb_all[i]
                    mask_fb_all_ = self.split_fb_mask(masks_fb)
                    masks_fb_ = self.squeeze(mask_fb_all_[k])
                    fb_mask_ = self.expand_dims(mask_, -1)
                    mask_fb_mask_ = self.cast(self.tile(self.cast(fb_mask_, mstype.int32), (1, 28, 28)), mstype.bool_)
                    masks_fb_ = self.select(mask_fb_mask_, masks_fb_, self.test_mask_fb_zeros)
                    mask_fb_sorted_ = self.gather(masks_fb_, topk_inds)
                    mask_fb_ = self.gather(mask_fb_sorted_, index_)
                    res_masks_fb_tuple += (mask_fb_,)

            res_boxes = self.concat(res_boxes_tuple)
            res_labels = self.concat(res_labels_tuple)
            res_masks = self.concat(res_masks_tuple)

            reshape_size = (self.num_classes - 1) * self.rpn_max_num
            res_boxes = self.reshape(res_boxes, (1, reshape_size, 5))
            res_labels = self.reshape(res_labels, (1, reshape_size, 1))
            res_masks = self.reshape(res_masks, (1, reshape_size, 1))

            all_bboxes += (res_boxes,)
            all_labels += (res_labels,)
            all_masks += (res_masks,)
            if self.with_mask:
                res_masks_fb = self.concat(res_masks_fb_tuple)
                res_masks_fb = self.reshape(res_masks_fb, (1, reshape_size, 28, 28))
                all_masks_fb += (res_masks_fb,)

        all_bboxes = self.concat(all_bboxes)
        all_labels = self.concat(all_labels)
        all_masks = self.concat(all_masks)

        if self.with_mask:
            all_masks_fb = self.concat(all_masks_fb)
            return all_bboxes, all_labels, all_masks, all_masks_fb

        return all_bboxes, all_labels, all_masks

    def construct_train(self, x, proposal, proposal_mask, gt_bboxes, gt_labels, gt_valids, gt_masks=None):
        """train construct of roi head"""
        gt_labels = self.cast(gt_labels, mstype.int32)
        gt_valids = self.cast(gt_valids, mstype.int32)
        bboxes_tuple = ()
        deltas_tuple = ()
        labels_tuple = ()
        mask_tuple = ()

        pos_bboxes_tuple = ()
        pos_mask_fb_tuple = ()
        pos_labels_tuple = ()
        pos_mask_tuple = ()

        for i in range(self.batch_size):
            gt_bboxes_i = self.squeeze(gt_bboxes[i:i + 1:1, ::])

            gt_labels_i = self.squeeze(gt_labels[i:i + 1:1, ::])
            gt_labels_i = self.cast(gt_labels_i, mstype.uint8)

            gt_valids_i = self.squeeze(gt_valids[i:i + 1:1, ::])
            gt_valids_i = self.cast(gt_valids_i, mstype.bool_)

            if self.with_mask:
                gt_masks_i = self.squeeze(gt_masks[i:i + 1:1, ::])
                gt_masks_i = self.cast(gt_masks_i, mstype.bool_)

                bboxes, deltas, labels, mask, pos_bboxes, pos_mask_fb, pos_labels, pos_mask = \
                    self.bbox_assigner_sampler_for_rcnn(
                        gt_bboxes_i, gt_labels_i, proposal_mask[i], proposal[i][::, 0:4:1], gt_valids_i, gt_masks_i
                    )
                pos_mask_fb_tuple += (pos_mask_fb,)
                pos_labels_tuple += (pos_labels,)
                pos_mask_tuple += (pos_mask,)
            else:
                bboxes, deltas, labels, mask, pos_bboxes = self.bbox_assigner_sampler_for_rcnn(
                    gt_bboxes_i, gt_labels_i, proposal_mask[i], proposal[i][::, 0:4:1], gt_valids_i
                )

            pos_bboxes_tuple += (pos_bboxes,)
            bboxes_tuple += (bboxes,)
            deltas_tuple += (deltas,)
            labels_tuple += (labels,)
            mask_tuple += (mask,)

        bbox_targets = self.concat(deltas_tuple)
        rcnn_labels = self.concat(labels_tuple)
        bbox_targets = F.stop_gradient(bbox_targets)
        rcnn_labels = F.stop_gradient(rcnn_labels)
        rcnn_labels = self.cast(rcnn_labels, mstype.int32)

        if self.batch_size > 1:
            bboxes_all = self.concat(bboxes_tuple)
            pos_bboxes_all = self.concat(pos_bboxes_tuple)
        else:
            bboxes_all = bboxes_tuple[0]
            pos_bboxes_all = pos_bboxes_tuple[0]

        rois = self.concat_1((self.roi_align_index_tensor, bboxes_all))

        rois = self.cast(rois, mstype.float32)
        rois = F.stop_gradient(rois)

        pos_rois = self.concat_1((self.roi_align_index_tensor_pos, pos_bboxes_all))
        pos_rois = self.cast(pos_rois, mstype.float32)
        pos_rois = F.stop_gradient(pos_rois)

        roi_feats = self.roi_align(
            rois, self.cast(x[0], mstype.float32), self.cast(x[1], mstype.float32),
            self.cast(x[2], mstype.float32), self.cast(x[3], mstype.float32)
        )

        roi_feats = self.cast(roi_feats, self.ms_type)
        rcnn_masks = self.concat(mask_tuple)
        rcnn_masks = F.stop_gradient(rcnn_masks)
        rcnn_mask_squeeze = self.squeeze(self.cast(rcnn_masks, mstype.bool_))
        _, rcnn_cls_loss, rcnn_reg_loss, _ = self.rcnn(roi_feats, bbox_targets,
                                                       rcnn_labels, rcnn_mask_squeeze)
        loss = rcnn_cls_loss + rcnn_reg_loss

        if self.with_mask:
            rcnn_pos_masks_fb = self.concat(pos_mask_fb_tuple)
            rcnn_pos_masks_fb = F.stop_gradient(rcnn_pos_masks_fb)
            rcnn_pos_labels = self.concat(pos_labels_tuple)
            rcnn_pos_labels = F.stop_gradient(rcnn_pos_labels)
            rcnn_pos_labels = self.cast(rcnn_pos_labels, mstype.int32)

            rcnn_pos_masks = self.concat(pos_mask_tuple)
            rcnn_pos_masks = F.stop_gradient(rcnn_pos_masks)
            rcnn_pos_mask_squeeze = self.squeeze(self.cast(rcnn_pos_masks, mstype.bool_))
            roi_feats_mask = self.roi_align_mask(
                pos_rois, self.cast(x[0], mstype.float32), self.cast(x[1], mstype.float32),
                self.cast(x[2], mstype.float32), self.cast(x[3], mstype.float32)
            )
            roi_feats_mask = self.cast(roi_feats_mask, mstype.float32)
            rcnn_mask_fb_loss = self.rcnn_mask(roi_feats_mask,
                                               rcnn_pos_labels,
                                               rcnn_pos_mask_squeeze,
                                               rcnn_pos_masks_fb)

            loss = loss + rcnn_mask_fb_loss

        return loss

    def construct_test(self, x, img_metas, proposal, proposal_mask):
        """construct test of roi_head"""
        bboxes_tuple = ()
        mask_tuple = ()
        mask_tuple += proposal_mask
        bbox_targets = proposal_mask
        rcnn_labels = proposal_mask

        for p_i in proposal:
            bboxes_tuple += (p_i[::, 0:4:1],)

        if self.test_batch_size > 1:
            bboxes_all = self.concat(bboxes_tuple)
        else:
            bboxes_all = bboxes_tuple[0]
        rois = self.concat_1((self.roi_align_index_test_tensor, bboxes_all))

        rois = F.stop_gradient(rois)

        roi_feats = self.roi_align_test(rois,
                                        self.cast(x[0], mstype.float32),
                                        self.cast(x[1], mstype.float32),
                                        self.cast(x[2], mstype.float32),
                                        self.cast(x[3], mstype.float32))
        roi_feats = self.cast(roi_feats, self.ms_type)
        rcnn_masks = self.concat(mask_tuple)
        rcnn_masks = F.stop_gradient(rcnn_masks)
        rcnn_mask_squeeze = self.squeeze(self.cast(rcnn_masks, mstype.bool_))

        _, rcnn_cls_loss, rcnn_reg_loss, _ = self.rcnn(roi_feats, bbox_targets, rcnn_labels, rcnn_mask_squeeze)

        if self.with_mask:
            mask_fb_pred_all = self.rcnn_mask_test(x, bboxes_all, rcnn_cls_loss, rcnn_reg_loss)

            mask_output = self.get_det_bboxes(rcnn_cls_loss, rcnn_reg_loss, \
                                              rcnn_masks, bboxes_all, img_metas, mask_fb_pred_all)
            return mask_output

        output = self.get_det_bboxes(rcnn_cls_loss, rcnn_reg_loss, rcnn_masks, bboxes_all, img_metas)
        return output

    def rcnn_mask_test(self, x, rois, cls_pred, reg_pred):
        """Prediction masks in an images by the bounding boxes
        """
        cls_scores = self.softmax(cls_pred / self.value)

        cls_scores_all = self.split(cls_scores)
        reg_pred = self.reshape(reg_pred, (-1, self.num_classes, 4))
        reg_pred_all = self.split(reg_pred)
        rois_all = self.split(rois)
        boxes_tuple = ()
        for i in range(self.test_batch_size):
            cls_score_max_index, _ = self.argmax_with_value(cls_scores_all[i])
            cls_score_max_index = self.cast(self.onehot(cls_score_max_index, self.num_classes,
                                                        self.on_value, self.off_value), mstype.float32)
            cls_score_max_index = self.expand_dims(cls_score_max_index, -1)
            cls_score_max_index = self.tile(cls_score_max_index, (1, 1, 4))
            reg_pred_max = reg_pred_all[i] * cls_score_max_index
            reg_pred_max = self.reducesum(reg_pred_max, 1)

            reg_pred_max = self.cast(reg_pred_max, mstype.float16)
            rois_i = self.cast(rois_all[i], mstype.float16)

            out_boxes_i = self.decode(rois_i, reg_pred_max)
            boxes_tuple += (out_boxes_i,)

        boxes_all = self.concat(boxes_tuple)
        boxes_rois = self.concat_1((self.roi_align_index_test_tensor, boxes_all))
        boxes_rois = self.cast(boxes_rois, mstype.float32)
        roi_feats_mask_test = self.roi_align_mask_test(boxes_rois,
                                                       self.cast(x[0], mstype.float32),
                                                       self.cast(x[1], mstype.float32),
                                                       self.cast(x[2], mstype.float32),
                                                       self.cast(x[3], mstype.float32))
        roi_feats_mask_test = self.cast(roi_feats_mask_test, mstype.float32)
        mask_fb_pred_all = self.rcnn_mask(roi_feats_mask_test)
        return mask_fb_pred_all
