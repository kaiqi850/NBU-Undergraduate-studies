# -*- coding: utf-8 -*-

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
"""the module is used to visualize image."""
import os

import cv2
import numpy as np
from datasets.utils.classes import get_classes


def img2vision(img_path, save_dir, bboxes, labels, masks,
               label_type="coco", score_thr=0.6, max_num=10):
    """Visualisize detection result for the picture
    Args:
        img_path (str):
            single image or image file path
        save_dir (str) :
            the path of saving image detection result
        bboxes :
            image detection boxes and scores of different classes
        labels:
            image detection label corresponding to bboxes
        masks:
            the mask of image detection boxes after nms
        label_type (tuple):
            dataset type,default is coco
        score_thr (float):
            the min score of image object box,default is 0.6
        max_num (int):
            the max detection boxes number in a picture,default is 10
    """

    assert bboxes.ndim == 2, \
        "bboxes ndim should be 2, but its ndim is {}".format(bboxes.ndim)

    assert labels.ndim == 1, \
        "labels ndim should be 1, but its ndim is {}".format(labels.ndim)

    assert bboxes.shape[0] == labels.shape[0], \
        "bboxes[0] should be equal to labels[0], bboxes[0] {} != labels[0] {}".format(bboxes.shape[0],
                                                                                      labels.shape[0])
    assert bboxes.shape[1] == 4 or bboxes.shape[1] == 5, \
        "bboxes[1] should be 4 or 5, but it's {}".format(bboxes.shape[1])

    classes = get_classes(label_type)

    bboxes_mask = bboxes[masks, :]
    labels_mask = labels[masks]

    if bboxes_mask.shape[0] > max_num:
        inds = np.argsort(-bboxes_mask[:, -1])
        inds = inds[:max_num]
        bboxes_mask = bboxes_mask[inds]
        labels_mask = labels_mask[inds]

    img = cv2.imread(img_path)
    img_name = img_path.split("/")[-1]
    for dets in enumerate(zip(bboxes_mask, labels_mask)):

        bboxes_new = dets[1][0]
        label = dets[1][1]
        bbox = bboxes_new[:4].astype(np.int32)
        score = bboxes_new[-1]

        if score > score_thr:
            cv2.rectangle(img, bbox[0:2], bbox[2:4], (0, 204, 0), 2)
            cv2.putText(img, "%s: %.3f" % (classes[label], score),
                        (bbox[0], bbox[1] + 15),
                        cv2.FONT_HERSHEY_COMPLEX, 0.7,
                        (0, 0, 255), thickness=2)
    new_name = "Det_" + img_name
    cv2.imwrite(os.path.join(save_dir, new_name), img)
