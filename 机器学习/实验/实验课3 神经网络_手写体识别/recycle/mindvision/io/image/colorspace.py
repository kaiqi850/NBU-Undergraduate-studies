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
"""color convert"""

import cv2


def bgr2gray(image, keepdim=False):
    """
    Convert a bgr image to grayscale image.

    Args:
        image (ndarray): The input image.
        keepdim (bool): If False then return the grayscale image with 2 dims, otherwise 3 dims.

    Returns:
        ndarray: The converted grayscale image.
    """
    out_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if keepdim:
        out_image = out_image[..., None]
    return out_image


def rgb2gray(img, keepdim=False):
    """Convert a RGB image to grayscale image.

    Args:
        img (ndarray): The input image.
        keepdim (bool): If False (by default), then return the grayscale image
            with 2 dims, otherwise 3 dims.

    Returns:
        ndarray: The converted grayscale image.
    """
    out_image = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    if keepdim:
        out_image = out_image[..., None]
    return out_image


def gray2bgr(img):
    """Convert a grayscale image to BGR image.

    Args:
        img (ndarray): The input image.

    Returns:
        ndarray: The converted BGR image.
    """
    img = img[..., None] if img.ndim == 2 else img
    out_image = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return out_image


def gray2rgb(img):
    """Convert a grayscale image to RGB image.

    Args:
        img (ndarray): The input image.

    Returns:
        ndarray: The converted RGB image.
    """
    img = img[..., None] if img.ndim == 2 else img
    out_image = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    return out_image
