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
"""RPN for FasterRCNN"""
import numpy as np

import mindspore.nn as nn
import mindspore.common.dtype as mstype
from mindspore import context, Tensor
from mindspore.ops import functional as F
from mindspore.ops import operations as P

from mindvision.detection.internals.anchor.anchor_generator import AnchorGenerator
from mindvision.detection.internals.bbox.assigner.bbox_assign_sample import BboxAssignSample
from mindvision.detection.models.builder import build_anchor
from mindvision.detection.models.meta_arch.base_detector import BaseDetector
from mindvision.detection.models.proposal.proposal_generator import Proposal

from mindvision.engine.class_factory import ClassFactory, ModuleType
from mindvision.engine.loss.cross_entropy_loss import CrossEntropyLoss
from mindvision.engine.loss.smooth_l1_loss import SmoothL1Loss


class RpnRegClsBlock(nn.Cell):
    """
    Rpn reg cls block for rpn layer

    Args:
        in_channels (int) - Input channels of shared convolution.
        feat_channels (int) - Output channels of shared convolution.
        num_anchors (int) - The anchor number.
        cls_out_channels (int) - Output channels of classification convolution.
        weight_conv (Tensor) - weight init for rpn conv.
        bias_conv (Tensor) - bias init for rpn conv.
        weight_cls (Tensor) - weight init for rpn cls conv.
        bias_cls (Tensor) - bias init for rpn cls conv.
        weight_reg (Tensor) - weight init for rpn reg conv.
        bias_reg (Tensor) - bias init for rpn reg conv.

    Returns:
        Tensor, output tensor.
    """

    def __init__(self,
                 in_channels,
                 feat_channels,
                 num_anchors,
                 cls_out_channels,
                 weight_conv,
                 bias_conv,
                 weight_cls,
                 bias_cls,
                 weight_reg,
                 bias_reg):
        super(RpnRegClsBlock, self).__init__()
        self.rpn_conv = nn.Conv2d(in_channels, feat_channels,
                                  kernel_size=3, stride=1, pad_mode='same',
                                  has_bias=True, weight_init=weight_conv, bias_init=bias_conv)
        self.relu = nn.ReLU()

        self.rpn_cls = nn.Conv2d(feat_channels, num_anchors * cls_out_channels,
                                 kernel_size=1, pad_mode='valid',
                                 has_bias=True, weight_init=weight_cls, bias_init=bias_cls)

        self.rpn_reg = nn.Conv2d(feat_channels, num_anchors * 4,
                                 kernel_size=1, pad_mode='valid',
                                 has_bias=True, weight_init=weight_reg, bias_init=bias_reg)

    def construct(self, x):
        """Construct RPN."""
        x = self.relu(self.rpn_conv(x))

        x1 = self.rpn_cls(x)
        x2 = self.rpn_reg(x)

        return x1, x2


@ClassFactory.register(ModuleType.HEAD)
class AnchorHead(BaseDetector):
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

    def __init__(self,
                 config,
                 anchor_generator,
                 feature_shapes,
                 batch_size,
                 num_anchors,
                 loss_cls,
                 loss_bbox,
                 train_cfg,
                 test_cfg,
                 ):
        super(AnchorHead, self).__init__()
        cfg_rpn = config
        self.anchor_gen = build_anchor(anchor_generator)
        self.anchor_list = self.anchor_gen.get_anchors(feature_shapes)

        self.proposal_generator = Proposal(train_cfg.proposal,
                                           train_cfg.batch_size,
                                           feature_shapes, True)
        self.proposal_generator_test = Proposal(test_cfg.proposal,
                                                test_cfg.test_batch_size,
                                                feature_shapes, False)
        self.dtype = np.float32
        self.ms_type = mstype.float32
        self.device_type = "Ascend" if context.get_context("device_target") == "Ascend" else "Others"
        self.num_bboxes = cfg_rpn.num_bboxes
        self.slice_index = ()
        self.feature_anchor_shape = ()
        self.slice_index += (0,)
        index = 0
        for shape in feature_shapes:
            self.slice_index += (self.slice_index[index] + shape[0] * shape[1] * num_anchors,)
            self.feature_anchor_shape += (shape[0] * shape[1] * num_anchors * batch_size,)
            index += 1

        self.gt_labels_stage1 = Tensor(np.ones((config.batch_size, config.num_gts)).astype(np.uint8))
        self.num_anchors = num_anchors
        self.batch_size = batch_size
        self.test_batch_size = test_cfg.test_batch_size
        self.num_layers = 5

        self.transpose = P.Transpose()
        self.reshape = P.Reshape()
        self.concat = P.Concat(axis=0)

        self.trans_shape = (0, 2, 3, 1)

        self.reshape_shape_reg = (-1, 4)
        self.reshape_shape_cls = (-1,)
        self.num_expected_total = Tensor(
            np.array(train_cfg.rpn.sampler.num_expected_neg * self.batch_size).astype(self.dtype)
        )
        self.get_targets = BboxAssignSample(
            train_cfg.rpn.assigner, train_cfg.rpn.sampler, config.num_gts,
            self.batch_size, self.num_bboxes, False
        )
        self.check_anchors = AnchorGenerator.check_anchors
        self.sum_loss = P.ReduceSum()
        self.loss_cls = P.SigmoidCrossEntropyWithLogits()
        self.loss_cls_ce = CrossEntropyLoss(use_sigmoid=True,
                                            reduction="mean",
                                            loss_weight=loss_cls.loss_weight)
        self.loss_smooth_l1 = SmoothL1Loss(beta=1.0 / 9.0,
                                           reduction="mean",
                                           loss_weight=loss_bbox.loss_weight)
        self.squeeze = P.Squeeze()
        self.cast = P.Cast()
        self.tile = P.Tile()
        self.zeros_like = P.ZerosLike()
        self.clsloss = Tensor(np.zeros((1,)).astype(self.dtype))
        self.regloss = Tensor(np.zeros((1,)).astype(self.dtype))

    def construct_train(self, rpn_cls_score_total, rpn_bbox_pred_total, img_metas, gt_bboxes, gt_valids):
        """
        Args:
            rpn_cls_score_total (list) - class score.
            rpn_bbox_pred_total (list) - class score.
            img_metas(list) - image shape info
            gt_bboxes(list) - ground truth bboxes
            gt_valids(list) - masks of ground truth
        Returns:
            clsloss, regloss, proposal, proposal_mask
        Examples:
            construct_train(rpn_cls_score_total, rpn_bbox_pred_total, img_metas, gt_bboxes, gt_valids)
        """
        gt_labels = self.gt_labels_stage1

        rpn_cls_score = ()
        rpn_bbox_pred = ()

        for i in range(self.num_layers):
            x1 = rpn_cls_score_total[i]
            x2 = rpn_bbox_pred_total[i]

            x1 = self.transpose(x1, self.trans_shape)
            x1 = self.reshape(x1, self.reshape_shape_cls)

            x2 = self.transpose(x2, self.trans_shape)
            x2 = self.reshape(x2, self.reshape_shape_reg)

            rpn_cls_score = rpn_cls_score + (x1,)
            rpn_bbox_pred = rpn_bbox_pred + (x2,)

        clsloss = self.clsloss
        regloss = self.regloss

        bbox_targets = ()
        bbox_weights = ()
        labels = ()
        label_weights = ()
        for i in range(self.batch_size):
            valid_anchor_mask_tuple = self.check_anchors(self.anchor_list, img_metas[i:i + 1:1, ::])

            anchors = self.concat(self.anchor_list)
            valid_anchor_masks = self.concat(valid_anchor_mask_tuple)

            gt_bboxes_i = self.squeeze(gt_bboxes[i:i + 1:1, ::])
            gt_labels_i = self.squeeze(gt_labels[i:i + 1:1, ::])
            gt_valids_i = self.squeeze(gt_valids[i:i + 1:1, ::])

            bbox_target, bbox_weight, label, label_weight = self.get_targets(gt_bboxes_i,
                                                                             gt_labels_i,
                                                                             valid_anchor_masks,
                                                                             anchors, gt_valids_i)
            bbox_target = self.cast(bbox_target, self.ms_type)
            bbox_weight = self.cast(bbox_weight, self.ms_type)
            label = self.cast(label, self.ms_type)
            label_weight = self.cast(label_weight, self.ms_type)

            for j in range(self.num_layers):
                begin = self.slice_index[j]
                end = self.slice_index[j + 1]
                stride = 1
                bbox_targets += (bbox_target[begin:end:stride, ::],)
                bbox_weights += (bbox_weight[begin:end:stride],)
                labels += (label[begin:end:stride],)
                label_weights += (label_weight[begin:end:stride],)

        for i in range(self.num_layers):
            bbox_target_using = ()
            bbox_weight_using = ()
            label_using = ()
            label_weight_using = ()

            for j in range(self.batch_size):
                bbox_target_using += (bbox_targets[i + (self.num_layers * j)],)
                bbox_weight_using += (bbox_weights[i + (self.num_layers * j)],)
                label_using += (labels[i + (self.num_layers * j)],)
                label_weight_using += (label_weights[i + (self.num_layers * j)],)

            bbox_target_with_batchsize = self.concat(bbox_target_using)
            bbox_weight_with_batchsize = self.concat(bbox_weight_using)
            label_with_batchsize = self.concat(label_using)
            label_weight_with_batchsize = self.concat(label_weight_using)

            bbox_target_ = F.stop_gradient(bbox_target_with_batchsize)
            bbox_weight_ = F.stop_gradient(bbox_weight_with_batchsize)
            label_ = F.stop_gradient(label_with_batchsize)
            label_weight_ = F.stop_gradient(label_weight_with_batchsize)

            cls_score_i = self.cast(rpn_cls_score[i], self.ms_type)
            reg_score_i = self.cast(rpn_bbox_pred[i], self.ms_type)

            bbox_weight_ = self.tile(self.reshape(bbox_weight_, (self.feature_anchor_shape[i], 1)), (1, 4))
            clsloss += self.loss_cls_ce(cls_score_i, label_, label_weight_, self.num_expected_total)
            regloss += self.loss_smooth_l1(reg_score_i, bbox_target_, bbox_weight_, self.num_expected_total)

        proposal, proposal_mask = self.proposal_generator(rpn_cls_score_total, rpn_bbox_pred_total, self.anchor_list)

        return clsloss, regloss, proposal, proposal_mask

    def construct_test(self, rpn_cls_score_total, rpn_bbox_pred_total):
        """Model test."""
        proposal, proposal_mask = self.proposal_generator_test(rpn_cls_score_total,
                                                               rpn_bbox_pred_total,
                                                               self.anchor_list)
        return proposal, proposal_mask
