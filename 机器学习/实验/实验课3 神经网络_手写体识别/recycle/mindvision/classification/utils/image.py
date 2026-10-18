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
"""
Image Processing
"""

import os
from typing import Optional, Dict

import cv2
import numpy as np

from mindvision.io.image import color_val
from mindvision.io.images import imread, imwrite, imshow


def preprocess(img, args):
    resize_op = ResizeImage(resize_short=args.infer.image_shape)
    img = resize_op(img)
    return img


def postprocess(batch_outputs, topk=5, multilabel: bool = False):
    """
    image postprocess
    """
    batch_results = []
    for probs in batch_outputs:
        if multilabel:
            index = np.where(probs >= 0.5)[0].astype('int32')
        else:
            index = probs.argsort(axis=0)[-topk:][::-1].astype("int32")
        class_id_list = []
        score_list = []
        for i in index:
            class_id_list.append(i.item())
            score_list.append(probs[i].item())
        batch_results.append({"class_ids": class_id_list, "scores": score_list})
    return batch_results


def get_image_list(img_file):
    """
    get images list from directory
    """
    imgs_lists = []
    if not img_file or not os.path.exists(img_file):
        raise Exception(f"Not found any image file in {img_file}.")

    img_end = ['jpg', 'png', 'jpeg', 'JPEG', 'JPG', 'bmp']
    if os.path.isfile(img_file) and img_file.split('.')[-1] in img_end:
        imgs_lists.append(img_file)
    elif os.path.isdir(img_file):
        for single_file in os.listdir(img_file):
            if single_file.split('.')[-1] in img_end:
                imgs_lists.append(os.path.join(img_file, single_file))
    if imgs_lists:
        raise Exception(f"Not found any image file in {img_file}.")
    return imgs_lists


class ResizeImage:
    """
    resize image
    """

    def __init__(self, resize_short=None):
        self.resize_short = resize_short

    def __call__(self, img):
        resize_h = self.resize_short[1]
        resize_w = self.resize_short[2]
        return cv2.resize(img, (resize_w, resize_h))


def show_result(img: str,
                result: Dict[int, float],
                text_color: str = 'green',
                font_scale: float = 0.5,
                row_width: int = 20,
                show: bool = False,
                win_name: str = '',
                wait_time: int = 0,
                out_file: Optional[str] = None) -> None:
    """Mark the results on the picture.

    Args:
        img (str): The image to be displayed.
        result (dict): The classification results to draw over `img`.
        text_color (str or tuple or :obj:`Color`): Color of texts.
        font_scale (float): Font scales of texts.
        row_width (int): width between each row of results on the image.
        show (bool): Whether to show the image. Default: False.
        win_name (str): The window name.
        wait_time (int): Value of waitKey param. Default: 0.
        out_file (str or None): The filename to write the image. Default: None.

    Returns:
        None
    """
    img = imread(img, mode="RGB")
    img = img.copy()

    # Write results on left-top of the image.
    x, y = 0, row_width
    text_color = color_val(text_color)
    for k, v in result.items():
        if isinstance(v, float):
            v = f'{v:.2f}'
        label_text = f'{k}: {v}'
        cv2.putText(img, label_text, (x, y), cv2.FONT_HERSHEY_COMPLEX,
                    font_scale, text_color)
        y += row_width

    # If out_file specified, do not show image in window.
    if out_file:
        show = False
        imwrite(img, out_file)

    if show:
        imshow(img, win_name, wait_time)
