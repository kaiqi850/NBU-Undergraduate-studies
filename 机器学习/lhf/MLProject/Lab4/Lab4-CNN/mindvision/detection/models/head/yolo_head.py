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
# ==============================================================================
""" Yolo head """

from abc import abstractmethod

import mindspore as ms
import mindspore.nn as nn
from mindspore.common.tensor import Tensor
from mindspore.ops import functional as F
from mindspore.ops import operations as P

from models.builder import build_anchor
from models.head.base_dense_head import BaseDenseHead
from internals.bbox.iou_calculator import Iou, Giou

from mindvision.engine.class_factory import ClassFactory, ModuleType
from mindvision.engine.loss.builder import build_loss
from mindvision.engine.utils.config import Config


class YoloHead(BaseDenseHead):
    """Yolo base head.

    Args:
        config (Config) :  The config options

    """

    def __init__(self, config):
        """Constructor for YoloHead"""
        super(YoloHead, self).__init__()
        self.detect_large = DetectorBlock('l', config, config.l_scale_x_y,
                                          config.l_offset_x_y)
        self.detect_mid = DetectorBlock('m', config, config.l_scale_x_y,
                                        config.l_offset_x_y)
        self.detect_small = DetectorBlock('s', config, config.s_scale_x_y,
                                          config.s_offset_x_y)
        self.training = config.is_training

    def loss(self, prediction, input_shape, *args):
        """ loss func for yolo detector. """
        output_large, output_mid, output_small = \
            prediction[0], prediction[1], prediction[2]
        y_true_0, y_true_1, y_true_2, gt_0, gt_1, gt_2 = \
            args[1], args[2], args[3], args[4], args[5], args[6]
        losses_large = self.loss_single(*output_large, y_true_0,
                                        gt_0, input_shape, self.anchors[0])
        losses_mid = self.loss_single(*output_mid, y_true_1,
                                      gt_1, input_shape, self.anchors[1])
        losses_small = self.loss_single(*output_small, y_true_2,
                                        gt_2, input_shape, self.anchors[2])
        loss = losses_large + losses_mid + losses_small * 0.2
        loss = P.ExpandDims()(loss, -1)
        return loss

    @abstractmethod
    def loss_single(self, grid, prediction, pred_xy, pred_wh,
                    y_true, gt_box, input_shape, anchors):
        pass

    def construct(self, feats, input_shape):
        output_large = self.detect_large(feats[0], input_shape)
        output_mid = self.detect_mid(feats[1], input_shape)
        output_small = self.detect_small(feats[2], input_shape)
        return output_large, output_mid, output_small


@ClassFactory.register(ModuleType.HEAD)
class YOLOv5Head(YoloHead):
    """The Head of YOLOv5
    Args:
        kwargs (dict) : head config
    Examples:
    """

    def __init__(self, **kwargs):
        """Constructor for Yolov5 Head"""
        super(YOLOv5Head, self).__init__(Config(**kwargs))
        config = Config(**kwargs)
        self.anchors = [
            build_anchor(config.anchor_generator).get_anchors(idx)
            for idx in config.anchor_generator.anchor_mask
        ]
        self.ignore_threshold = Tensor(config.ignore_threshold, ms.float32)
        self.concat = P.Concat(axis=-1)
        self.iou = Iou()
        self.reduce_max = P.ReduceMax(keep_dims=False)
        self.confidence_loss = build_loss(config.loss_confidence)
        self.class_loss = build_loss(config.loss_cls)

        self.reduce_sum = P.ReduceSum()
        self.giou = Giou()

    def loss_single(self, grid, prediction, pred_xy, pred_wh,
                    y_true, gt_box, input_shape, anchors):
        """
        Args:
            grid: yolo grid.
            prediction: origin output from yolo.
            pred_xy: (sigmoid(xy)+grid)/grid_size.
            pred_wh: (exp(wh)*anchors)/input_shape.
            y_true : after normalize.
            gt_box: [batch, maxboxes, xyhw] after normalize.
            input_shape: input data shape.
            anchors: input anchors.
        """
        object_mask = y_true[:, :, :, :, 4:5]
        class_probs = y_true[:, :, :, :, 5:]
        true_boxes = y_true[:, :, :, :, :4]

        grid_shape = P.Shape()(prediction)[1:3]
        grid_shape = P.Cast()(F.tuple_to_array(grid_shape[::-1]), ms.float32)

        pred_boxes = self.concat((pred_xy, pred_wh))
        true_wh = y_true[:, :, :, :, 2:4]
        true_wh = P.Select()(P.Equal()(true_wh, 0.0),
                             P.Fill()(P.DType()(true_wh),
                                      P.Shape()(true_wh), 1.0),
                             true_wh)
        true_wh = P.Log()(true_wh / anchors * input_shape)
        box_loss_scale = 2 - y_true[:, :, :, :, 2:3] * y_true[:, :, :, :, 3:4]

        gt_shape = P.Shape()(gt_box)
        gt_box = P.Reshape()(gt_box, (gt_shape[0], 1, 1, 1, gt_shape[1], gt_shape[2]))

        iou = self.iou(P.ExpandDims()(pred_boxes, -2), gt_box)
        best_iou = self.reduce_max(iou, -1)

        # ignore_mask IOU too small
        ignore_mask = best_iou < self.ignore_threshold
        ignore_mask = P.Cast()(ignore_mask, ms.float32)
        ignore_mask = P.ExpandDims()(ignore_mask, -1)
        ignore_mask = F.stop_gradient(ignore_mask)

        confidence_loss = self.confidence_loss(object_mask, prediction[:, :, :, :, 4:5], ignore_mask)
        class_loss = self.class_loss(object_mask, prediction[:, :, :, :, 5:], class_probs)

        object_mask_me = P.Reshape()(object_mask, (-1, 1))
        box_loss_scale_me = P.Reshape()(box_loss_scale, (-1, 1))
        pred_boxes_me = xywh2x1y1x2y2(pred_boxes)
        pred_boxes_me = P.Reshape()(pred_boxes_me, (-1, 4))
        true_boxes_me = xywh2x1y1x2y2(true_boxes)
        true_boxes_me = P.Reshape()(true_boxes_me, (-1, 4))
        c_iou = self.giou(pred_boxes_me, true_boxes_me)
        c_iou_loss = object_mask_me * box_loss_scale_me * (1 - c_iou)
        c_iou_loss_me = self.reduce_sum(c_iou_loss, ())
        loss = c_iou_loss_me * 4 + confidence_loss + class_loss
        batch_size = P.Shape()(prediction)[0]
        return loss / batch_size


@ClassFactory.register(ModuleType.HEAD)
class YOLOv4Head(YoloHead):
    """The Head of YOLOv4
    Args:
        kwargs (dict) : head config
    Examples:
    """

    def __init__(self, **kwargs):
        """Constructor for Yolov4 Head"""
        super(YOLOv4Head, self).__init__(Config(**kwargs))
        config = Config(**kwargs)
        self.anchors = [
            build_anchor(config.anchor_generator).get_anchors(idx)
            for idx in config.anchor_generator.anchor_mask
        ]
        self.ignore_threshold = Tensor(config.ignore_threshold, ms.float32)
        self.concat = P.Concat(axis=-1)
        self.iou = Iou()
        self.reduce_max = P.ReduceMax(keep_dims=False)
        self.confidence_loss = build_loss(config.loss_confidence)
        self.class_loss = build_loss(config.loss_cls)

        self.reduce_sum = P.ReduceSum()
        self.giou = Giou()

    def loss_single(self, grid, prediction, pred_xy, pred_wh,
                    y_true, gt_box, input_shape, anchors):
        """
        Args:
            grid: yolo grid.
            prediction: origin output from yolo.
            pred_xy: (sigmoid(xy)+grid)/grid_size.
            pred_wh: (exp(wh)*anchors)/input_shape.
            y_true : after normalize.
            gt_box: [batch, maxboxes, xyhw] after normalize.
            input_shape: input data shape.
            anchors: input anchors.
        """
        object_mask = y_true[:, :, :, :, 4:5]
        class_probs = y_true[:, :, :, :, 5:]
        true_boxes = y_true[:, :, :, :, :4]

        # 2-w*h for large picture, use small scale,
        # since small obj need more precise
        box_loss_scale = 2 - y_true[:, :, :, :, 2:3] * y_true[:, :, :, :, 3:4]

        pred_boxes = self.concat((pred_xy, pred_wh))
        gt_shape = P.Shape()(gt_box)
        gt_box = P.Reshape()(gt_box, (gt_shape[0], 1, 1, 1, gt_shape[1],
                                      gt_shape[2]))

        # add one more dimension for broadcast
        iou = self.iou(P.ExpandDims()(pred_boxes, -2), gt_box)
        # gt_box is x,y,h,w after normalize
        # [batch, grid[0], grid[1], num_anchor, num_gt]
        best_iou = self.reduce_max(iou, -1)
        # [batch, grid[0], grid[1], num_anchor]

        # ignore_mask IOU too small
        ignore_mask = best_iou < self.ignore_threshold
        ignore_mask = P.Cast()(ignore_mask, ms.float32)
        ignore_mask = P.ExpandDims()(ignore_mask, -1)
        # ignore_mask backpro will cause a lot maximunGrad and
        # minimumGrad time consume.
        # so we turn off its gradient
        ignore_mask = F.stop_gradient(ignore_mask)

        box_confidence = prediction[:, :, :, :, 4:5]
        box_probs = prediction[:, :, :, :, 5:]

        conf_weight = object_mask + (1 - object_mask) * ignore_mask
        confidence_loss = self.confidence_loss(box_confidence, object_mask, conf_weight)
        class_loss = self.class_loss(box_probs, class_probs, object_mask)

        object_mask_me = P.Reshape()(object_mask, (-1, 1))  # [8, 72, 72, 3, 1]
        box_loss_scale_me = P.Reshape()(box_loss_scale, (-1, 1))
        pred_boxes_me = xywh2x1y1x2y2(pred_boxes)
        pred_boxes_me = P.Reshape()(pred_boxes_me, (-1, 4))
        true_boxes_me = xywh2x1y1x2y2(true_boxes)
        true_boxes_me = P.Reshape()(true_boxes_me, (-1, 4))
        ciou = self.giou(pred_boxes_me, true_boxes_me)
        ciou_loss = object_mask_me * box_loss_scale_me * (1 - ciou)
        ciou_loss_me = self.reduce_sum(ciou_loss, ())
        loss = ciou_loss_me * 10 + confidence_loss + class_loss
        batch_size = P.Shape()(prediction)[0]
        return loss / batch_size


@ClassFactory.register(ModuleType.HEAD)
class YOLOv3Head(YoloHead):
    """The Head of YOLOv3

    Args:
        kwargs (dict) : head config
    Examples:
    """

    def __init__(self, **kwargs):
        """Constructor for YOLOv3Head"""
        super(YOLOv3Head, self).__init__(Config(**kwargs))
        config = Config(**kwargs)
        self.anchors = [
            build_anchor(config.anchor_generator).get_anchors(idx)
            for idx in config.anchor_generator.anchor_mask
        ]
        self.ignore_threshold = Tensor(config.ignore_threshold, ms.float32)
        self.concat = P.Concat(axis=-1)
        self.iou = Iou()
        self.reduce_max = P.ReduceMax(keep_dims=False)
        self.xy_loss = build_loss(config.loss_xy)
        self.wh_loss = build_loss(config.loss_wh)
        self.confidence_loss = build_loss(config.loss_confidence)
        self.class_loss = build_loss(config.loss_cls)

    def loss_single(self, grid, prediction, pred_xy, pred_wh,
                    y_true, gt_box, input_shape, anchors):
        # prediction : origin output from yolo
        # pred_xy: (sigmoid(xy)+grid)/grid_size
        # pred_wh: (exp(wh)*anchors)/input_shape
        # y_true : after normalize
        # gt_box: [batch, maxboxes, xyhw] after normalize

        object_mask = y_true[:, :, :, :, 4:5]
        class_probs = y_true[:, :, :, :, 5:]

        grid_shape = P.Shape()(prediction)[1:3]
        grid_shape = P.Cast()(F.tuple_to_array(grid_shape[::-1]), ms.float32)

        pred_boxes = self.concat((pred_xy, pred_wh))
        true_xy = y_true[:, :, :, :, :2] * grid_shape - grid
        true_wh = y_true[:, :, :, :, 2:4]
        true_wh = P.Select()(
            P.Equal()(true_wh, 0.0),
            P.Fill()(P.DType()(true_wh), P.Shape()(true_wh), 1.0),
            true_wh
        )
        true_wh = P.Log()(true_wh / anchors * input_shape)
        # 2-w*h for large picture, use small scale, since small obj need more precise
        box_loss_scale = 2 - y_true[:, :, :, :, 2:3] * y_true[:, :, :, :, 3:4]

        gt_shape = P.Shape()(gt_box)
        gt_box = P.Reshape()(gt_box, (gt_shape[0], 1, 1, 1, gt_shape[1], gt_shape[2]))

        # add one more dimension for broadcast
        iou = self.iou(P.ExpandDims()(pred_boxes, -2), gt_box)
        # gt_box is x,y,h,w after normalize
        # [batch, grid[0], grid[1], num_anchor, num_gt]
        best_iou = self.reduce_max(iou, -1)
        # [batch, grid[0], grid[1], num_anchor]

        # ignore_mask IOU too small
        ignore_mask = best_iou < self.ignore_threshold
        ignore_mask = P.Cast()(ignore_mask, ms.float32)
        ignore_mask = P.ExpandDims()(ignore_mask, -1)
        # ignore_mask backpro will cause a lot maximunGrad and minimumGrad time consume.
        # so we turn off its gradient
        ignore_mask = F.stop_gradient(ignore_mask)

        box_xy = prediction[:, :, :, :, :2]
        box_wh = prediction[:, :, :, :, 2:4]
        box_confidence = prediction[:, :, :, :, 4:5]
        box_probs = prediction[:, :, :, :, 5:]

        xy_loss = self.xy_loss(box_xy, true_xy, object_mask * box_loss_scale)
        wh_loss = self.wh_loss(box_wh, true_wh, object_mask * box_loss_scale)
        conf_weight = object_mask + (1 - object_mask) * ignore_mask
        confidence_loss = self.confidence_loss(box_confidence,
                                               object_mask, conf_weight)
        class_loss = self.class_loss(box_probs, class_probs, object_mask)
        loss = xy_loss + wh_loss + confidence_loss + class_loss
        batch_size = P.Shape()(prediction)[0]
        return loss / batch_size


class DetectorBlock(nn.Cell):
    """The detector of YOLO.

     Args:
         scale: Character.
         config: Configuration.
         is_training: Bool, Whether train or not, default True.
         scale_x_y: scale
         offset_x_y: offset

     Returns:
         Tuple, tuple of output tensor,(f1,f2,f3).

     Examples:
         DetectionBlock(scale='l',stride=32)
     """

    def __init__(self, scale, config, scale_x_y=1, offset_x_y=0, is_training=True):
        super(DetectorBlock, self).__init__()
        self.config = config
        if scale == 's':
            idx = (0, 1, 2)
        elif scale == 'm':
            idx = (3, 4, 5)
        elif scale == 'l':
            idx = (6, 7, 8)
        else:
            raise KeyError("Invalid scale value for DetectionBlock.")
        self.anchors = build_anchor(config.anchor_generator).get_anchors(idx)
        self.num_anchors_per_scale = 3
        self.num_attrib = 4 + 1 + self.config.num_classes
        self.lambda_coord = 1

        self.sigmoid = nn.Sigmoid()
        self.reshape = P.Reshape()
        self.tile = P.Tile()
        self.concat = P.Concat(axis=-1)
        self.training = is_training
        self.scale_x_y = scale_x_y
        self.offset_x_y = offset_x_y

    def construct(self, x, input_shape):
        """Construct method"""
        num_batch = P.Shape()(x)[0]
        grid_size = P.Shape()(x)[2:4]

        # Reshape and transpose the feature to
        # [n, grid_size[0], grid_size[1], 3, num_attrib]
        prediction = P.Reshape()(
            x, (num_batch, self.num_anchors_per_scale,
                self.num_attrib, grid_size[0], grid_size[1])
        )
        prediction = P.Transpose()(prediction, (0, 3, 4, 1, 2))

        range_x = range(grid_size[1])
        range_y = range(grid_size[0])
        grid_x = P.Cast()(F.tuple_to_array(range_x), ms.float32)
        grid_y = P.Cast()(F.tuple_to_array(range_y), ms.float32)
        # Tensor of shape [grid_size[0], grid_size[1], 1, 1] representing the coordinate of x/y axis for each grid
        # [batch, gridx, gridy, 1, 1]
        grid_x = self.tile(self.reshape(grid_x, (1, 1, -1, 1, 1)),
                           (1, grid_size[0], 1, 1, 1))
        grid_y = self.tile(self.reshape(grid_y, (1, -1, 1, 1, 1)),
                           (1, 1, grid_size[1], 1, 1))
        # Shape is [grid_size[0], grid_size[1], 1, 2]
        grid = self.concat((grid_x, grid_y))

        box_xy = prediction[:, :, :, :, :2]
        box_wh = prediction[:, :, :, :, 2:4]
        box_confidence = prediction[:, :, :, :, 4:5]
        box_probs = prediction[:, :, :, :, 5:]

        # gridsize1 is x
        # gridsize0 is y
        box_xy = \
            (self.scale_x_y * self.sigmoid(box_xy) - self.offset_x_y + grid) / \
            P.Cast()(F.tuple_to_array((grid_size[1], grid_size[0])), ms.float32)
        # box_wh is w->h
        box_wh = P.Exp()(box_wh) * self.anchors / input_shape
        box_confidence = self.sigmoid(box_confidence)
        box_probs = self.sigmoid(box_probs)

        if self.training:
            return grid, prediction, box_xy, box_wh
        return self.concat((box_xy, box_wh, box_confidence, box_probs))


def xywh2x1y1x2y2(box_xywh):
    boxes_x1 = box_xywh[..., 0:1] - box_xywh[..., 2:3] / 2
    boxes_y1 = box_xywh[..., 1:2] - box_xywh[..., 3:4] / 2
    boxes_x2 = box_xywh[..., 0:1] + box_xywh[..., 2:3] / 2
    boxes_y2 = box_xywh[..., 1:2] + box_xywh[..., 3:4] / 2
    boxes_x1y1x2y2 = P.Concat(-1)((boxes_x1, boxes_y1, boxes_x2, boxes_y2))

    return boxes_x1y1x2y2
