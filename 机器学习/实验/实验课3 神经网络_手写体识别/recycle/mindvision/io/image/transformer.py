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

import numpy as np

class CropImage:
    """crop image"""

    def __init__(self, size):
        if isinstance(size, int):
            self.size = (size, size)
        else:
            self.size = size

    def __call__(self, img):
        w, h = self.size
        img_h, img_w = img.shape[:2]
        w_start = (img_w - w) // 2
        h_start = (img_h - h) // 2

        w_end = w_start + w
        h_end = h_start + h
        return img[h_start:h_end, w_start:w_end, :]


class NormalizeImage:
    """normalize image."""

    def __init__(self, scale=None, mean=None, std=None):
        self.scale = np.float32(scale if scale else 1.0 / 255.0)
        mean = mean if mean else [0.485, 0.456, 0.406]
        std = std if std else [0.229, 0.224, 0.225]

        shape = (1, 1, 3)
        self.mean = np.array(mean).reshape(shape).astype('float32')
        self.std = np.array(std).reshape(shape).astype('float32')

    def __call__(self, img):
        return (img.astype('float32') * self.scale - self.mean) / self.std
