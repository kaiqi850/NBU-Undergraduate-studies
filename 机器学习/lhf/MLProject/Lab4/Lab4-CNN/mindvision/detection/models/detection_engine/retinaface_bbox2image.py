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
""" Retinaface DetectionEngine  """
import json
import os
import numpy as np

from mindvision.engine.class_factory import ClassFactory, ModuleType

def decode_bbox(bbox, priors, var):
    """decode coordinate.

    Parameters
    ----------
    bbox : numpy.ndarray
        An ndarray with shape :math:`(N, 4)`.
    priors : numpy.ndarray
        An ndarray with shape :math:`(M, 4)`.
    var : float or int, default is 0
    Returns
    -------
    numpy.ndarray
        An ndarray with shape :math:（N, 4）
        bounding boxes coordinate（x0, y0, x1, y1 ）

    """
    boxes = np.concatenate((
        priors[:, 0:2] + bbox[:, 0:2] * var[0] * priors[:, 2:4],
        priors[:, 2:4] * np.exp(bbox[:, 2:4] * var[1])), axis=1)
    boxes[:, :2] -= boxes[:, 2:] / 2
    boxes[:, 2:] += boxes[:, :2]
    return boxes


@ClassFactory.register(ModuleType.DETECTION_ENGINE)
class RetinafaceDetectionEngine:
    """ Retinaface DetectionEngine. """
    def __init__(self, nms_thresh, conf_thresh, iou_thresh, var, batch_size, gt_dir, label_txt, eval_imageid_file):
        self.results = {}
        self.nms_thresh = nms_thresh
        self.conf_thresh = conf_thresh
        self.iou_thresh = iou_thresh
        self.var = var
        self.batch_szie = batch_size
        self.gt_dir = gt_dir
        self.label_txt = label_txt
        self.eval_imageid_file = eval_imageid_file

    def _iou(self, a, b):
        """ Calculate iou. """
        a0 = a.shape[0]
        b0 = b.shape[0]
        max_xy = np.minimum(
            np.broadcast_to(np.expand_dims(a[:, 2:4], 1), [a0, b0, 2]),
            np.broadcast_to(np.expand_dims(b[:, 2:4], 0), [a0, b0, 2]))
        min_xy = np.maximum(
            np.broadcast_to(np.expand_dims(a[:, 0:2], 1), [a0, b0, 2]),
            np.broadcast_to(np.expand_dims(b[:, 0:2], 0), [a0, b0, 2]))
        inter = np.maximum((max_xy - min_xy + 1), np.zeros_like(max_xy - min_xy))
        inter = inter[:, :, 0] * inter[:, :, 1]

        area_a = np.broadcast_to(
            np.expand_dims(
                (a[:, 2] - a[:, 0] + 1) * (a[:, 3] - a[:, 1] + 1), 1),
            np.shape(inter))
        area_b = np.broadcast_to(
            np.expand_dims(
                (b[:, 2] - b[:, 0] + 1) * (b[:, 3] - b[:, 1] + 1), 0),
            np.shape(inter))
        union = area_a + area_b - inter
        return inter / union

    def _nms(self, boxes, threshold=0.5):
        """NMS"""
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]
        scores = boxes[:, 4]

        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = scores.argsort()[::-1]

        reserved_boxes = []
        while order.size > 0:
            i = order[0]
            reserved_boxes.append(i)
            max_x1 = np.maximum(x1[i], x1[order[1:]])
            max_y1 = np.maximum(y1[i], y1[order[1:]])
            min_x2 = np.minimum(x2[i], x2[order[1:]])
            min_y2 = np.minimum(y2[i], y2[order[1:]])

            intersect_w = np.maximum(0.0, min_x2 - max_x1 + 1)
            intersect_h = np.maximum(0.0, min_y2 - max_y1 + 1)
            intersect_area = intersect_w * intersect_h
            ovr = intersect_area / (areas[i] + areas[order[1:]] - intersect_area)

            indices = np.where(ovr <= threshold)[0]
            order = order[indices + 1]

        return reserved_boxes

    def detect(self, args, **kwargs):
        """attain and save predict bboxes.

        Parameters
        ----------
        args:
        args[0]: boxes.
        args[1]: confs.
        val: value.
        kwargs["image_id"]: image_id
        kwargs['resize']: image_resize
        kwargs["scale"]: image_scale
        kwargs["priors"]: priors
        Returns
        -------
        Dict:
        each image :bounding boxes coordinate（x0, y0, x1, y1 ）

        """
        boxes = args[0]
        confs = args[1]
        image_id = kwargs["image_id"].asnumpy()
        for j in range(self.batch_szie):
            resize = kwargs['resize'].asnumpy()[j]
            scale = kwargs["scale"].asnumpy()[j]
            priors = kwargs["priors"].asnumpy()[j]
            with open(self.eval_imageid_file, 'r') as load_f:
                load_dict = json.load(load_f)
                for k, v in load_dict.items():
                    if image_id[j] == v:
                        image_path = k
            if boxes.shape[0] == 0:
                # add to result
                event_name, img_name = image_path.split('/')
                self.results[event_name][img_name[:-4]] = {'img_path': image_path,
                                                           'bboxes': []}
                return

            boxes = decode_bbox(np.squeeze(boxes.asnumpy()[j:j + 1, :, :], 0), priors, self.var)
            boxes = boxes * scale / resize

            scores = np.squeeze(confs.asnumpy()[j:j + 1, :, :], 0)[:, 1]
            # ignore low scores
            inds = np.where(scores > self.conf_thresh)[0]
            boxes = boxes[inds]
            scores = scores[inds]

            # keep top-K before NMS
            order = scores.argsort()[::-1]
            boxes = boxes[order]
            scores = scores[order]

            # do NMS
            dets = np.hstack((boxes, scores[:, np.newaxis])).astype(np.float32, copy=False)
            keep = self._nms(dets, self.nms_thresh)
            dets = dets[keep, :]

            dets[:, 2:4] = (dets[:, 2:4].astype(np.int) - dets[:, 0:2].astype(np.int)).astype(np.float)  # int
            dets[:, 0:4] = dets[:, 0:4].astype(np.int).astype(np.float)                                  # int

            # add to result
            name = image_path.split('/')
            event_name = name[-2]
            img_name = name[-1]

            if event_name not in self.results.keys():
                self.results[event_name] = {}
            self.results[event_name][img_name[:-4]] = {'img_path': image_path,
                                                       'bboxes': dets[:, :5].astype(np.float).tolist()}

    def _get_gt_boxes(self):
        """get GT different levels of detection difficulty """
        from scipy.io import loadmat
        gt = loadmat(os.path.join(self.gt_dir, 'wider_face_val.mat'))
        hard = loadmat(os.path.join(self.gt_dir, 'wider_hard_val.mat'))
        medium = loadmat(os.path.join(self.gt_dir, 'wider_medium_val.mat'))
        easy = loadmat(os.path.join(self.gt_dir, 'wider_easy_val.mat'))
        annotations = {}
        annotations['faceboxes'] = gt['face_bbx_list']
        annotations['events'] = gt['event_list']
        annotations['files'] = gt['file_list']

        annotations['hard_gt_list'] = hard['gt_list']
        annotations['medium_gt_list'] = medium['gt_list']
        annotations['easy_gt_list'] = easy['gt_list']

        return annotations

    def _norm_pre_score(self):
        """Normalize predict scores"""
        max_score = 0
        min_score = 1

        for event in self.results:
            for name in self.results[event].keys():
                bbox = np.array(self.results[event][name]['bboxes']).astype(np.float)
                if bbox.shape[0] <= 0:
                    continue
                max_score = max(max_score, np.max(bbox[:, -1]))
                min_score = min(min_score, np.min(bbox[:, -1]))

        length = max_score - min_score
        for event in self.results:
            for name in self.results[event].keys():
                bbox = np.array(self.results[event][name]['bboxes']).astype(np.float)
                if bbox.shape[0] <= 0:
                    continue
                bbox[:, -1] -= min_score
                bbox[:, -1] /= length
                self.results[event][name]['bboxes'] = bbox.tolist()

    def _image_eval(self, predict, gt, keep, iou_thresh, section_num):
        """match predict bbox with GT"""
        predict_copy = predict.copy()
        gt_copy = gt.copy()

        image_p_right = np.zeros(predict_copy.shape[0])
        image_gt_right = np.zeros(gt_copy.shape[0])
        proposal = np.ones(predict_copy.shape[0])

        # x1y1wh -> x1y1x2y2
        predict_copy[:, 2:4] = predict_copy[:, 0:2] + predict_copy[:, 2:4]
        gt_copy[:, 2:4] = gt_copy[:, 0:2] + gt_copy[:, 2:4]

        ious = self._iou(predict_copy[:, 0:4], gt_copy[:, 0:4])
        for i in range(predict_copy.shape[0]):
            gt_ious = ious[i, :]
            max_iou, max_index = gt_ious.max(), gt_ious.argmax()
            if max_iou >= iou_thresh:
                if keep[max_index] == 0:
                    image_gt_right[max_index] = -1
                    proposal[i] = -1
                elif image_gt_right[max_index] == 0:
                    image_gt_right[max_index] = 1

            right_index = np.where(image_gt_right == 1)[0]
            image_p_right[i] = len(right_index)

        image_pr = np.zeros((section_num, 2), dtype=np.float)
        for section in range(section_num):
            thresh_section = 1 - (section + 1)/section_num
            over_score_index = np.where(predict[:, 4] >= thresh_section)[0]
            if over_score_index.shape[0] <= 0:
                image_pr[section, 0] = 0
                image_pr[section, 1] = 0
            else:
                index = over_score_index[-1]
                p_num = len(np.where(proposal[0:(index + 1)] == 1)[0])
                image_pr[section, 0] = p_num
                image_pr[section, 1] = image_p_right[index]

        return image_pr

    def get_eval_result(self):
        """Get outputs."""
        self._norm_pre_score()
        annotations = self._get_gt_boxes()
        facebox_list = annotations['faceboxes']
        event_list = annotations['events']
        file_list = annotations['files']
        hard_gt_list = annotations['hard_gt_list']
        medium_gt_list = annotations['medium_gt_list']
        easy_gt_list = annotations['easy_gt_list']

        section_num = 1000
        sets = ['easy', 'medium', 'hard']
        set_gts = [easy_gt_list, medium_gt_list, hard_gt_list]
        ap_key_dict = {0: "Easy   Val AP : ", 1: "Medium Val AP : ", 2: "Hard   Val AP : "}
        ap_dict = {}
        for each_set in range(len(sets)):
            gt_list = set_gts[each_set]
            count_gt = 0
            pr_curve = np.zeros((section_num, 2), dtype=np.float)
            for i, _ in enumerate(event_list):
                event = str(event_list[i][0][0])
                image_list = file_list[i][0]
                event_predict_dict = self.results[event]
                event_gt_index_list = gt_list[i][0]
                event_gt_box_list = facebox_list[i][0]

                for j, _ in enumerate(image_list):
                    predict = np.array(event_predict_dict[str(image_list[j][0][0])]['bboxes']).astype(np.float)
                    gt_boxes = event_gt_box_list[j][0].astype('float')
                    keep_index = event_gt_index_list[j][0]
                    count_gt += len(keep_index)

                    if gt_boxes.shape[0] <= 0 or predict.shape[0] <= 0:
                        continue
                    keep = np.zeros(gt_boxes.shape[0])
                    if keep_index.shape[0] > 0:
                        keep[keep_index - 1] = 1

                    image_pr = self._image_eval(predict, gt_boxes, keep,
                                                iou_thresh=self.iou_thresh,
                                                section_num=section_num)
                    pr_curve += image_pr

            precision = pr_curve[:, 1] / pr_curve[:, 0]
            recall = pr_curve[:, 1] / count_gt

            precision = np.concatenate((np.array([0.]), precision, np.array([0.])))
            recall = np.concatenate((np.array([0.]), recall, np.array([1.])))
            for i in range(precision.shape[0]-1, 0, -1):
                precision[i - 1] = np.maximum(precision[i - 1], precision[i])
            index = np.where(recall[1:] != recall[:-1])[0]
            ap = np.sum((recall[index + 1] - recall[index]) * precision[index + 1])

            print(ap_key_dict[each_set] + '{:.4f}'.format(ap))

        return ap_dict
