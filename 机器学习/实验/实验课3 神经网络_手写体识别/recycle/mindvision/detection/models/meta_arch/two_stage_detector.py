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
"""FasterRcnn based on ResNet50."""

from models.builder import build_backbone, build_neck, build_head
from models.meta_arch.base_detector import BaseDetector


class TwoStageDetector(BaseDetector):
    """FasterRcnn Network.

    Params:
        backbone: config of backbone
        neck: config of neck
        rpn_head: config of rpn_head
        roi_head: config of roi_head
        train_cfg: config of train
        test_cfg: config of test

    Returns:
        Tuple, tuple of output tensor.
        rpn_loss: Scalar, Total loss of RPN subnet.
        rcnn_loss: Scalar, Total loss of RCNN subnet.
        rpn_cls_loss: Scalar, Classification loss of RPN subnet.
        rpn_reg_loss: Scalar, Regression loss of RPN subnet.
        rcnn_cls_loss: Scalar, Classification loss of RCNN subnet.
        rcnn_reg_loss: Scalar, Regression loss of RCNN subnet.

    Examples:
        net = TwoStageDetector(config, backbone, neck, rpn_head, roi_head, train_cfg, test_cfg)
    """

    def __init__(self, config, backbone, neck, rpn_head, roi_head, train_cfg, test_cfg):
        super(TwoStageDetector, self).__init__()
        # config
        self.config = config
        # backbone
        self.backbone = build_backbone(backbone)
        # fpn
        if neck is not None:
            self.neck = build_neck(neck)
        # rpn and rpn loss
        if train_cfg is not None:
            rpn_head.update(train_cfg=train_cfg)
            roi_head.update(train_cfg=train_cfg)
        if test_cfg is not None:
            rpn_head.update(test_cfg=test_cfg)
            roi_head.update(test_cfg=test_cfg)

        self.rpn_head = build_head(rpn_head)
        self.roi_head = build_head(roi_head)

    def construct(self, img_data, img_metas, gt_bboxes=None, gt_labels=None, gt_valids=None, gt_masks=None):
        """Construct of two stage detector."""
        x = self.backbone(img_data)
        if self.has_neck:
            x = self.neck(x)

        if self.training:
            rpn_cls_loss, rpn_reg_loss, proposal, proposal_mask = \
                self.rpn_head.construct_train(x, img_metas, gt_bboxes, gt_valids)

            head_loss = self.roi_head.construct_train(
                x, proposal, proposal_mask, gt_bboxes, gt_labels, gt_valids, gt_masks
            )
            return rpn_cls_loss + rpn_reg_loss + head_loss

        proposal, proposal_mask = self.rpn_head.construct_test(x)
        output = self.roi_head.construct_test(x, img_metas, proposal, proposal_mask)
        return output
