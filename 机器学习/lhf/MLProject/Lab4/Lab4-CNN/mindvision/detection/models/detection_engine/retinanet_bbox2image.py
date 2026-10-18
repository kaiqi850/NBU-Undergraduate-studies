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
""" Retinanet COCO Detection Engine. """

import json

import numpy as np
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval

from mindvision.engine.class_factory import ClassFactory, ModuleType


@ClassFactory.register(ModuleType.DETECTION_ENGINE)
class RetinaDetectionEngine:
    """ RetinaNet COCO Detection Engine. """

    def __init__(self, ann_file, test_batch_size, num_classes, min_score, nms_thershold, max_boxes):
        self.outputs = []
        self.ann_file = ann_file
        self.test_batch_size = test_batch_size
        self.num_classes = num_classes
        self.min_score = min_score
        self.nms_thershold = nms_thershold
        self.max_boxes = max_boxes
        self.predictions = []
        self.img_ids = []
        val_cls = ["background", "person", "bicycle", "car", "motorcycle", "airplane", "bus",
                   "train", "truck", "boat", "traffic light", "fire hydrant",
                   "stop sign", "parking meter", "bench", "bird", "cat", "dog",
                   "horse", "sheep", "cow", "elephant", "bear", "zebra",
                   "giraffe", "backpack", "umbrella", "handbag", "tie",
                   "suitcase", "frisbee", "skis", "snowboard", "sports ball",
                   "kite", "baseball bat", "baseball glove", "skateboard",
                   "surfboard", "tennis racket", "bottle", "wine glass", "cup",
                   "fork", "knife", "spoon", "bowl", "banana", "apple",
                   "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza",
                   "donut", "cake", "chair", "couch", "potted plant", "bed",
                   "dining table", "toilet", "tv", "laptop", "mouse", "remote",
                   "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
                   "refrigerator", "book", "clock", "vase", "scissors",
                   "teddy bear", "hair drier", "toothbrush"]
        self.val_cls_dict = {}
        for i, cls in enumerate(val_cls):
            self.val_cls_dict[i] = cls
        self.coco_gt = COCO(self.ann_file)
        self.classs_dict = {}
        cat_ids = self.coco_gt.loadCats(self.coco_gt.getCatIds())
        for cat in cat_ids:
            self.classs_dict[cat["name"]] = cat["id"]

    def detect(self, output, **kwargs):
        """Postprocess the detection results."""
        pred_data = []
        img_metas = kwargs['image_shape']
        img_id = kwargs['image_id']
        for batch_idx in range(self.test_batch_size):
            h, w, _ = img_metas[batch_idx].asnumpy()
            pred_data.append({"boxes": output[0].asnumpy()[batch_idx],
                              "box_scores": output[1].asnumpy()[batch_idx],
                              "img_id": int(img_id.asnumpy()[batch_idx][0]),
                              "image_shape": [h, w]})

        for sample in pred_data:
            pred_boxes = sample['boxes']
            box_scores = sample['box_scores']
            img_id = sample['img_id']
            h, w = sample['image_shape']

            final_boxes = []
            final_label = []
            final_score = []
            self.img_ids.append(img_id)

            for c in range(1, self.num_classes):
                class_box_scores = box_scores[:, c]
                score_mask = class_box_scores > self.min_score
                class_box_scores = class_box_scores[score_mask]
                class_boxes = pred_boxes[score_mask] * [w, h, w, h]
                if score_mask.any():
                    nms_index = self.apply_nms(class_boxes, class_box_scores, self.nms_thershold, self.max_boxes)
                    class_boxes = class_boxes[nms_index]
                    class_box_scores = class_box_scores[nms_index]
                    final_boxes += class_boxes.tolist()
                    final_score += class_box_scores.tolist()
                    final_label += [self.classs_dict[self.val_cls_dict[c]]] * len(class_box_scores)
            for loc, label, score in zip(final_boxes, final_label, final_score):
                res = {}
                res['image_id'] = img_id
                res['bbox'] = [loc[0], loc[1], loc[2] - loc[0], loc[3] - loc[1]]
                res['score'] = score
                res['category_id'] = label
                self.predictions.append(res)

    def get_eval_result(self):
        """Obtain the evaluation results."""
        with open('predictions.json', 'w') as f:
            json.dump(self.predictions, f)
        coco_dt = self.coco_gt.loadRes('predictions.json')
        eval_results = COCOeval(self.coco_gt, coco_dt, iouType='bbox')
        eval_results.params.imgIds = self.img_ids
        eval_results.evaluate()
        eval_results.accumulate()
        eval_results.summarize()
        print("\n========================================\n")

    def apply_nms(self, all_boxes, all_scores, thres, max_boxes):
        """Apply NMS to bboxes."""
        x1 = all_boxes[:, 0]
        y1 = all_boxes[:, 1]
        x2 = all_boxes[:, 2]
        y2 = all_boxes[:, 3]
        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = all_scores.argsort()[::-1]
        keep = []

        while order.size > 0:
            i = order[0]
            keep.append(i)

            if len(keep) >= max_boxes:
                break

            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0.0, xx2 - xx1 + 1)
            h = np.maximum(0.0, yy2 - yy1 + 1)
            inter = w * h
            ovr = inter / (areas[i] + areas[order[1:]] - inter)

            inds = np.where(ovr <= thres)[0]

            order = order[inds + 1]
        return keep
