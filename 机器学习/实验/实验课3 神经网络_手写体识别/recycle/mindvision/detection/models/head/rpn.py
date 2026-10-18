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
import mindspore.common.dtype as mstype
import mindspore.nn as nn
from mindspore import context
from mindspore.common.initializer import initializer

from mindvision.detection.models.head.anchor_head import AnchorHead
from mindvision.engine.class_factory import ClassFactory, ModuleType


class RpnRegClsBlock(nn.Cell):
    """Rpn reg cls block for rpn layer.

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
class RPNHead(AnchorHead):
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
                 in_channels,
                 feat_channels,
                 num_anchors,
                 cls_out_channels,
                 loss_cls,
                 loss_bbox,
                 train_cfg,
                 test_cfg,
                 ):
        super(RPNHead, self).__init__(config, anchor_generator, feature_shapes,
                                      batch_size, num_anchors, loss_cls,
                                      loss_bbox, train_cfg, test_cfg)
        self.ms_type = mstype.float32
        self.device_type = "Ascend" if context.get_context("device_target") == "Ascend" else "Others"
        self.num_anchors = num_anchors
        self.num_layers = 5

        self.rpn_convs_list = nn.layer.CellList(
            self._make_rpn_layer(
                self.num_layers, in_channels, feat_channels, num_anchors, cls_out_channels
            )
        )

    def _make_rpn_layer(self, num_layers, in_channels, feat_channels, num_anchors, cls_out_channels):
        """Make rpn layer for rpn proposal network.

        Args:
        num_layers (int) - layer num.
        in_channels (int) - Input channels of shared convolution.
        feat_channels (int) - Output channels of shared convolution.
        num_anchors (int) - The anchor number.
        cls_out_channels (int) - Output channels of classification convolution.

        Returns:
        List, list of RpnRegClsBlock cells.
        """
        rpn_layer = []

        shp_weight_conv = (feat_channels, in_channels, 3, 3)
        shp_bias_conv = (feat_channels,)
        weight_conv = initializer('Normal', shape=shp_weight_conv, dtype=self.ms_type).to_tensor()
        bias_conv = initializer(0, shape=shp_bias_conv, dtype=self.ms_type).to_tensor()

        shp_weight_cls = (num_anchors * cls_out_channels, feat_channels, 1, 1)
        shp_bias_cls = (num_anchors * cls_out_channels,)
        weight_cls = initializer('Normal', shape=shp_weight_cls, dtype=self.ms_type).to_tensor()
        bias_cls = initializer(0, shape=shp_bias_cls, dtype=self.ms_type).to_tensor()

        shp_weight_reg = (num_anchors * 4, feat_channels, 1, 1)
        shp_bias_reg = (num_anchors * 4,)
        weight_reg = initializer('Normal', shape=shp_weight_reg, dtype=self.ms_type).to_tensor()
        bias_reg = initializer(0, shape=shp_bias_reg, dtype=self.ms_type).to_tensor()

        for i in range(num_layers):
            rpn_reg_cls_block = RpnRegClsBlock(in_channels, feat_channels, num_anchors, cls_out_channels,
                                               weight_conv, bias_conv, weight_cls,
                                               bias_cls, weight_reg, bias_reg)
            if self.device_type == "Ascend":
                rpn_reg_cls_block.to_float(mstype.float16)
            rpn_layer.append(rpn_reg_cls_block)

        for i in range(1, num_layers):
            rpn_layer[i].rpn_conv.weight = rpn_layer[0].rpn_conv.weight
            rpn_layer[i].rpn_cls.weight = rpn_layer[0].rpn_cls.weight
            rpn_layer[i].rpn_reg.weight = rpn_layer[0].rpn_reg.weight

            rpn_layer[i].rpn_conv.bias = rpn_layer[0].rpn_conv.bias
            rpn_layer[i].rpn_cls.bias = rpn_layer[0].rpn_cls.bias
            rpn_layer[i].rpn_reg.bias = rpn_layer[0].rpn_reg.bias

        return rpn_layer

    def construct_train(self, inputs, img_metas, gt_bboxes, gt_valids):
        """Construct Train."""
        rpn_cls_score_total, rpn_bbox_pred_total = self.get_cls_and_bbox(inputs)
        return super(RPNHead, self).construct_train(rpn_cls_score_total, rpn_bbox_pred_total,
                                                    img_metas, gt_bboxes, gt_valids)

    def construct_test(self, inputs):
        """Construct Test."""
        rpn_cls_score_total, rpn_bbox_pred_total = self.get_cls_and_bbox(inputs)
        return super(RPNHead, self).construct_test(rpn_cls_score_total, rpn_bbox_pred_total)

    def get_cls_and_bbox(self, inputs):
        """Get object class and bboxes."""
        rpn_cls_score_total = ()
        rpn_bbox_pred_total = ()
        for i in range(self.num_layers):
            x1, x2 = self.rpn_convs_list[i](inputs[i])
            rpn_cls_score_total = rpn_cls_score_total + (x1,)
            rpn_bbox_pred_total = rpn_bbox_pred_total + (x2,)
        return rpn_cls_score_total, rpn_bbox_pred_total
