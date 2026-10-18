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
""" Common COCO Detection Engine. """
import numpy as np
from pycocotools.coco import COCO

from mindvision.detection.utils.coco_utils import bbox2result_1image, coco_eval, results2json, get_seg_masks
from mindvision.engine.class_factory import ClassFactory, ModuleType


@ClassFactory.register(ModuleType.DETECTION_ENGINE)
class CommonDetectionEngine:
    """ Common COCO Detection Engine. """

    def __init__(self, ann_file, test_batch_size, num_classes, max_num, with_mask):
        self.outputs = []
        self.ann_file = ann_file
        self.test_batch_size = test_batch_size
        self.num_classes = num_classes
        self.max_num = max_num
        self.with_mask = with_mask

    def get_eval_result(self):
        """Obtain the evaluation results."""
        dataset_coco = COCO(self.ann_file)
        if self.with_mask:
            eval_types = ["bbox", "segm"]
        else:
            eval_types = ["bbox"]
        result_files = results2json(dataset_coco, self.outputs, "./results.pkl")
        coco_eval(result_files, eval_types, dataset_coco, single_result=False)

    def detect(self, output, **kwargs):
        """Postprocess the detection results."""
        all_bbox = output[0]
        all_label = output[1]
        all_mask = output[2]
        img_metas = kwargs['image_shape']
        if self.with_mask:
            all_mask_fb = output[3]

        for j in range(self.test_batch_size):
            all_bbox_squee = np.squeeze(all_bbox.asnumpy()[j, :, :])
            all_label_squee = np.squeeze(all_label.asnumpy()[j, :, :])
            all_mask_squee = np.squeeze(all_mask.asnumpy()[j, :, :])

            all_bboxes_tmp_mask = all_bbox_squee[all_mask_squee, :]
            all_labels_tmp_mask = all_label_squee[all_mask_squee]

            if self.with_mask:
                all_mask_fb_squee = np.squeeze(all_mask_fb.asnumpy()[j, :, :, :])
                all_mask_fb_tmp_mask = all_mask_fb_squee[all_mask_squee, :, :]

            if all_bboxes_tmp_mask.shape[0] > self.max_num:
                inds = np.argsort(-all_bboxes_tmp_mask[:, -1])
                inds = inds[:self.max_num]
                all_bboxes_tmp_mask = all_bboxes_tmp_mask[inds]
                all_labels_tmp_mask = all_labels_tmp_mask[inds]
                if self.with_mask:
                    all_mask_fb_tmp_mask = all_mask_fb_tmp_mask[inds]

            bbox_results = bbox2result_1image(all_bboxes_tmp_mask, all_labels_tmp_mask, self.num_classes)

            if self.with_mask:
                segm_results = get_seg_masks(all_mask_fb_tmp_mask, all_bboxes_tmp_mask, \
                                             all_labels_tmp_mask, img_metas[j], True, self.num_classes, 0.5)
                self.outputs.append((bbox_results, segm_results))
            else:
                self.outputs.append(bbox_results)
