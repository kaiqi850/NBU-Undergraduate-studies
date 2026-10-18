# Copyright 2020-21 Huawei Technologies Co., Ltd
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
"""centerface head"""

import mindspore as ms
import mindspore.nn as nn
from mindspore.common import dtype as mstype
from mindspore.ops import functional as F
from mindspore.ops import operations as P

from mindvision.engine.class_factory import ClassFactory, ModuleType
from mindvision.engine.loss.centerface_losses import FocalLoss, SmoothL1LossNew, SmoothL1LossNewCMask
from mindvision.engine.utils.config import Config


def conv1x1(in_channels, out_channels, stride=1, padding=0, has_bias=False):
    """conv1x1"""
    return nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, has_bias=has_bias,
                     padding=padding, pad_mode="pad")


@ClassFactory.register(ModuleType.HEAD)
class CenterFaceHead(nn.Cell):
    """centerface head"""

    def __init__(self, **kwargs):
        super(CenterFaceHead, self).__init__(Config(**kwargs))
        config = Config(**kwargs)

        self.wh_weight = config.loss_cls.loss_weight
        self.off_weight = config.loss_reg.loss_weight
        self.hm_weight = config.loss_off.loss_weight
        self.lm_weight = config.loss_cmask.loss_weight

        self.hm_head = nn.SequentialCell([conv1x1(64, 1, has_bias=True),
                                          nn.Sigmoid().add_flags_recursive(fp32=True)])
        self.wh_head = conv1x1(64, 2, has_bias=True)
        self.off_head = conv1x1(64, 2, has_bias=True)
        self.kps_head = conv1x1(64, 10, has_bias=True)
        self.expand_dims = P.ExpandDims()

        self.cls_loss = FocalLoss()
        self.reg_loss = SmoothL1LossNew()
        self.reg_loss_cmask = SmoothL1LossNewCMask()

        self.maxpool2d = P.MaxPoolWithArgmax(kernel_size=3, strides=1, pad_mode='same')
        self.topk = P.TopK(sorted=True)
        self.reshape = P.Reshape()
        self.test_batch = 1
        self.k = 200

    def construct_train(self, x, *args):
        """centerface head construct_train"""
        hm = args[1]
        reg_mask = args[2]
        ind = args[3]
        wh = args[4]
        wight_mask = args[5]
        hm_offset = args[6]
        hps_mask = args[7]
        landmarks = args[8]

        output_hm = self.hm_head(x)
        output_wh = self.wh_head(x)
        output_off = self.off_head(x)
        output_kps = self.kps_head(x)

        hm_loss = self.cls_loss(output_hm, hm)  # 1. focal loss, center points
        wh_loss = self.reg_loss(output_wh, ind, wh, wight_mask)  # 2. weight and height
        off_loss = self.reg_loss(output_off, ind, hm_offset, wight_mask)  # 3. offset
        lm_loss = self.reg_loss_cmask(output_kps, hps_mask, ind, landmarks)  # 4. landmark loss

        loss = self.hm_weight * hm_loss + self.wh_weight * wh_loss + self.off_weight * off_loss \
               + self.lm_weight * lm_loss

        # depend is needed when wight_mask and reg_mask is not been used
        F.depend(loss, F.sqrt(F.cast(wight_mask, mstype.float32)))
        F.depend(loss, F.sqrt(F.cast(reg_mask, mstype.float32)))

        loss = self.expand_dims(loss, -1)

        return loss

    # pylint: disable=unused-argument
    def construct_test(self, x, *args):
        """centerface head construct_test"""
        output_hm = self.hm_head(x)
        output_wh = self.wh_head(x)
        output_off = self.off_head(x)
        output_kps = self.kps_head(x)

        output_hm_nms, _ = self.maxpool2d(output_hm)
        abs_error = P.Abs()(output_hm - output_hm_nms)
        abs_out = P.Abs()(output_hm)
        error = abs_error / (abs_out + 1e-12)

        keep = P.Select()(P.LessEqual()(error, 1e-3), \
                          P.Fill()(ms.float32, P.Shape()(error), 1.0), \
                          P.Fill()(ms.float32, P.Shape()(error), 0.0))
        output_hm = output_hm * keep

        scores = self.reshape(output_hm, (self.test_batch, -1))
        topk_scores, topk_inds = self.topk(scores, self.k)

        return topk_scores, output_wh, output_off, output_kps, topk_inds
