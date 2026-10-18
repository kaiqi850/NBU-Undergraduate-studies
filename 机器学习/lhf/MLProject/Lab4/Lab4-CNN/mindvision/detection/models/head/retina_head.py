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
"""head for RetinaNet"""

import mindspore.common.dtype as mstype
import mindspore.nn as nn
from mindspore.ops import functional as F
from mindspore.ops import operations as P

from mindvision.engine.class_factory import ClassFactory, ModuleType
from mindvision.engine.loss.sigmoid_focal_loss import SigmoidFocalClassificationLoss
from mindvision.engine.loss.smooth_l1_loss import SmoothL1Loss


class FlattenConcat(nn.Cell):
    """
    Concatenate predictions into a single tensor.

    Args:
        config (dict): The default config of retinanet.

    Returns:
        Tensor, flatten predictions.
    """

    def __init__(self, num_retinanet_boxes):
        super(FlattenConcat, self).__init__()
        self.num_retinanet_boxes = num_retinanet_boxes
        self.concat = P.Concat(axis=1)
        self.transpose = P.Transpose()

    def construct(self, inputs):
        """train construct of flattenconcat"""
        output = ()
        batch_size = F.shape(inputs[0])[0]
        for x in inputs:
            x = self.transpose(x, (0, 2, 3, 1))
            output += (F.reshape(x, (batch_size, -1)),)
        res = self.concat(output)
        return F.reshape(res, (batch_size, self.num_retinanet_boxes, -1))


def ClassificationModel(in_channel, num_anchors, num_classes=81, feature_size=256):
    """classification branch of retinanet head"""
    conv1 = nn.Conv2d(in_channel, feature_size, kernel_size=3, pad_mode='same')
    conv2 = nn.Conv2d(feature_size, feature_size, kernel_size=3, pad_mode='same')
    conv3 = nn.Conv2d(feature_size, feature_size, kernel_size=3, pad_mode='same')
    conv4 = nn.Conv2d(feature_size, feature_size, kernel_size=3, pad_mode='same')
    conv5 = nn.Conv2d(feature_size, num_anchors * num_classes, kernel_size=3, pad_mode='same')
    return nn.SequentialCell([conv1, nn.ReLU(), conv2, nn.ReLU(), conv3, nn.ReLU(), conv4, nn.ReLU(), conv5])


def RegressionModel(in_channel, num_anchors, feature_size=256):
    """regression branch of retinanet head"""
    conv1 = nn.Conv2d(in_channel, feature_size, kernel_size=3, pad_mode='same')
    conv2 = nn.Conv2d(feature_size, feature_size, kernel_size=3, pad_mode='same')
    conv3 = nn.Conv2d(feature_size, feature_size, kernel_size=3, pad_mode='same')
    conv4 = nn.Conv2d(feature_size, feature_size, kernel_size=3, pad_mode='same')
    conv5 = nn.Conv2d(feature_size, num_anchors * 4, kernel_size=3, pad_mode='same')
    return nn.SequentialCell([conv1, nn.ReLU(), conv2, nn.ReLU(), conv3, nn.ReLU(), conv4, nn.ReLU(), conv5])


class MultiBox(nn.Cell):
    """
    Multibox conv layers. Each multibox layer contains class conf scores and localization predictions.

    Args:
        config (dict): The default config of retinanet.

    Returns:
        Tensor, localization predictions.
        Tensor, class conf scores.
    """

    def __init__(self, extras_out_channels, num_default, num_retinanet_boxes):
        super(MultiBox, self).__init__()

        out_channels = extras_out_channels
        num_default = num_default
        loc_layers = []
        cls_layers = []
        for k, out_channel in enumerate(out_channels):
            loc_layers += [RegressionModel(in_channel=out_channel, num_anchors=num_default[k])]
            cls_layers += [ClassificationModel(in_channel=out_channel, num_anchors=num_default[k])]

        self.multi_loc_layers = nn.layer.CellList(loc_layers)
        self.multi_cls_layers = nn.layer.CellList(cls_layers)
        self.flatten_concat = FlattenConcat(num_retinanet_boxes)

    def construct(self, inputs):
        loc_outputs = ()
        cls_outputs = ()
        for i in range(len(self.multi_loc_layers)):
            loc_outputs += (self.multi_loc_layers[i](inputs[i]),)
            cls_outputs += (self.multi_cls_layers[i](inputs[i]),)
        return self.flatten_concat(loc_outputs), self.flatten_concat(cls_outputs)


@ClassFactory.register(ModuleType.HEAD)
class RetinaHead(nn.Cell):
    """"
    Provide retinanet training loss through network.

    Args:
        network (Cell): The training network.
        config (dict): retinanet config.

    Returns:
        Tensor, the loss of the network.
    """

    def __init__(self, gamma, alpha, extras_out_channels, num_default, num_retinanet_boxes):
        super(RetinaHead, self).__init__()
        self.less = P.Less()
        self.tile = P.Tile()
        self.reduce_sum = P.ReduceSum()
        self.reduce_mean = P.ReduceMean()
        self.expand_dims = P.ExpandDims()
        self.class_loss = SigmoidFocalClassificationLoss(gamma, alpha)
        self.loc_loss = SmoothL1Loss(beta=1.0, reduction="mean", index=(1, 2))
        self.cast = P.Cast()

        self.prior_scaling_xy = 0.1
        self.prior_scaling_wh = 0.2
        self.multi_box = MultiBox(extras_out_channels, num_default, num_retinanet_boxes)
        self.multi_box.to_float(mstype.float16)

    def construct_train(self, x, *args):
        """train construct of retinanet head"""
        gt_loc = args[2]
        gt_label = args[3]
        num_matched_boxes = args[4]
        pred_loc, pred_label = self.multi_box(x)
        pred_loc = self.cast(pred_loc, mstype.float32)
        pred_label = self.cast(pred_label, mstype.float32)

        mask = F.cast(self.less(0, gt_label), mstype.float32)
        num_matched_boxes = self.reduce_sum(F.cast(num_matched_boxes, mstype.float32))

        # Localization Loss
        mask_loc = self.tile(self.expand_dims(mask, -1), (1, 1, 4))
        loss_loc = self.loc_loss(pred_loc, gt_loc, mask_loc, 4)

        # Classification Loss
        loss_cls = self.class_loss(pred_label, gt_label)
        return self.reduce_sum((loss_cls + loss_loc) / num_matched_boxes)

    def construct_test(self, x, *args):
        """test construct of retinanet head"""
        default_boxes = args[2]
        pred_loc, pred_label = self.multi_box(x)

        default_bbox_xy = default_boxes[..., :2]
        default_bbox_wh = default_boxes[..., 2:]
        pred_xy = pred_loc[..., :2] * self.prior_scaling_xy * default_bbox_wh + default_bbox_xy
        pred_wh = P.Exp()(pred_loc[..., 2:] * self.prior_scaling_wh) * default_bbox_wh

        pred_xy_0 = pred_xy - pred_wh / 2.0
        pred_xy_1 = pred_xy + pred_wh / 2.0
        pred_xy = P.Concat(-1)((pred_xy_0, pred_xy_1))
        pred_xy = P.Maximum()(pred_xy, 0)
        pred_xy = P.Minimum()(pred_xy, 1)

        return pred_xy, pred_label
