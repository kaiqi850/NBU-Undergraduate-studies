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
"""FasterRcnn Rcnn network."""

import mindspore.common.dtype as mstype
import mindspore.nn as nn
import numpy as np
from mindspore import context
from mindspore.common.initializer import initializer
from mindspore.common.parameter import Parameter
from mindspore.common.tensor import Tensor
from mindspore.ops import operations as P

from mindvision.engine.loss.cross_entropy_loss import CrossEntropyLoss
from mindvision.engine.loss.smooth_l1_loss import SmoothL1Loss


class DenseNoTranpose(nn.Cell):
    """Dense method"""

    def __init__(self, input_channels, output_channels, weight_init):
        super(DenseNoTranpose, self).__init__()
        self.weight = Parameter(initializer(weight_init, [input_channels, output_channels], mstype.float32))
        self.bias = Parameter(initializer("zeros", [output_channels], mstype.float32))

        self.matmul = P.MatMul(transpose_b=False)
        self.bias_add = P.BiasAdd()
        self.cast = P.Cast()
        self.device_type = "Ascend" if context.get_context("device_target") == "Ascend" else "Others"

    def construct(self, x):
        """Model construct."""
        if self.device_type == "Ascend":
            x = self.cast(x, mstype.float16)
            weight = self.cast(self.weight, mstype.float16)
            bias = self.cast(self.bias, mstype.float16)
            output = self.bias_add(self.matmul(x, weight), bias)
        else:
            output = self.bias_add(self.matmul(x, self.weight), self.bias)
        return output


class Rcnn(nn.Cell):
    """Rcnn subnet.

    Args:
        config (dict) - Config.
        representation_size (int) - Channels of shared dense.
        batch_size (int) - Batchsize.
        num_classes (int) - Class number.
        target_means (list) - Means for encode function. Default: (.0, .0, .0, .0]).
        target_stds (list) - Stds for encode function. Default: (0.1, 0.1, 0.2, 0.2).

    Returns:
        Tuple, tuple of output tensor.

    Examples:
        Rcnn(config=config, representation_size = 1024, batch_size=2, num_classes = 81, \
             target_means=(0., 0., 0., 0.), target_stds=(0.1, 0.1, 0.2, 0.2))
    """

    def __init__(self,
                 rcnn,
                 representation_size,
                 num_classes,
                 num_boxes,
                 target_means=(0., 0., 0., 0.),
                 target_stds=(0.1, 0.1, 0.2, 0.2)):
        super(Rcnn, self).__init__()
        cfg = rcnn
        self.dtype = np.float32
        self.ms_type = mstype.float32
        self.rcnn_loss_cls_weight = Tensor(np.array(cfg.rcnn_loss_cls_weight).astype(self.dtype))
        self.rcnn_loss_reg_weight = Tensor(np.array(cfg.rcnn_loss_reg_weight).astype(self.dtype))
        self.rcnn_fc_out_channels = cfg.rcnn_fc_out_channels
        self.target_means = target_means
        self.target_stds = target_stds
        self.num_classes = num_classes
        self.in_channels = cfg.rcnn_in_channels

        shape_0 = (self.rcnn_fc_out_channels, representation_size)
        weights_0 = initializer("XavierUniform", shape=shape_0[::-1], dtype=self.ms_type).to_tensor()
        shape_1 = (self.rcnn_fc_out_channels, self.rcnn_fc_out_channels)
        weights_1 = initializer("XavierUniform", shape=shape_1[::-1], dtype=self.ms_type).to_tensor()
        self.shared_fc_0 = DenseNoTranpose(representation_size, self.rcnn_fc_out_channels, weights_0)
        self.shared_fc_1 = DenseNoTranpose(self.rcnn_fc_out_channels, self.rcnn_fc_out_channels, weights_1)

        cls_weight = initializer('Normal', shape=[num_classes, self.rcnn_fc_out_channels][::-1],
                                 dtype=self.ms_type).to_tensor()
        reg_weight = initializer('Normal', shape=[num_classes * 4, self.rcnn_fc_out_channels][::-1],
                                 dtype=self.ms_type).to_tensor()
        self.cls_scores = DenseNoTranpose(self.rcnn_fc_out_channels, num_classes, cls_weight)
        self.reg_scores = DenseNoTranpose(self.rcnn_fc_out_channels, num_classes * 4, reg_weight)

        self.flatten = P.Flatten()
        self.relu = P.ReLU()
        self.logicaland = P.LogicalAnd()
        self.loss_cls_func = CrossEntropyLoss(use_sigmoid=False, reduction="mean",
                                              loss_weight=cfg.rcnn_loss_cls_weight)
        self.loss_reg_func = SmoothL1Loss(beta=1.0, reduction="mean",
                                          loss_weight=cfg.rcnn_loss_reg_weight)
        self.reshape = P.Reshape()
        self.onehot = P.OneHot()
        self.greater = P.Greater()
        self.cast = P.Cast()
        self.sum_loss = P.ReduceSum()
        self.tile = P.Tile()
        self.expandims = P.ExpandDims()

        self.gather = P.GatherNd()
        self.argmax = P.ArgMaxWithValue(axis=1)

        self.on_value = Tensor(1.0, mstype.float32)
        self.off_value = Tensor(0.0, mstype.float32)
        self.value = Tensor(1.0, self.ms_type)

        # (cfg.num_expected_pos_stage2 + cfg.num_expected_neg_stage2) * batch_size
        self.num_bboxes = num_boxes

        rmv_first = np.ones((self.num_bboxes, self.num_classes))
        rmv_first[:, 0] = np.zeros((self.num_bboxes,))
        self.rmv_first_tensor = Tensor(rmv_first.astype(self.dtype))

    def construct(self, featuremap, bbox_targets, labels, mask):
        """Construct of rcnn."""
        x = self.flatten(featuremap)

        x = self.relu(self.shared_fc_0(x))
        x = self.relu(self.shared_fc_1(x))

        x_cls = self.cast(self.cls_scores(x), mstype.float32)
        x_reg = self.cast(self.reg_scores(x), mstype.float32)
        if self.training:
            bbox_weights = self.cast(
                self.logicaland(self.greater(labels, 0), mask), mstype.int32
            ) * labels

            labels = self.onehot(labels, self.num_classes, self.on_value, self.off_value)
            bbox_targets = self.tile(self.expandims(bbox_targets, 1), (1, self.num_classes, 1))
            mask = self.cast(mask, mstype.float32)
            loss_cls = self.loss_cls_func(x_cls, labels, mask, self.sum_loss(mask, (0,)))
            bbox_weights = self.cast(
                self.onehot(bbox_weights, self.num_classes, self.on_value, self.off_value),
                self.ms_type
            )
            bbox_weights = bbox_weights * self.rmv_first_tensor
            pos_bbox_pred = self.reshape(x_reg, (self.num_bboxes, -1, 4))
            bbox_weights = P.Tile()(
                bbox_weights.reshape(bbox_weights.shape[0], bbox_weights.shape[1], 1), (1, 1, 4)
            )
            loss_reg = self.loss_reg_func(
                pos_bbox_pred, bbox_targets, bbox_weights, self.sum_loss(mask, (0,))
            )

            loss = self.rcnn_loss_cls_weight * loss_cls + self.rcnn_loss_reg_weight * loss_reg
            loss_print = (loss_cls, loss_reg)

            out = (loss, loss_cls, loss_reg, loss_print)
        else:
            out = (x_cls, (x_cls / self.value), x_reg, x_cls)

        return out
