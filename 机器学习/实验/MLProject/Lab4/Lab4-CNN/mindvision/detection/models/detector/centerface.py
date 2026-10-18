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
"""CenterFace"""
from mindspore.train.serialization import load_checkpoint, load_param_into_net
from models.meta_arch.one_stage_detector import OneStageDetector

from mindvision.engine.class_factory import ClassFactory, ModuleType
from mindvision.log import info


@ClassFactory.register(ModuleType.DETECTOR)
class CenterFace(OneStageDetector):
    """CenterFace detection module"""

    def init_weights(self, ckpt_path):
        """Full model weights initialization."""
        param_dict = load_checkpoint(ckpt_path)
        info("Full Network param dict:\n {}".format(param_dict))
        load_param_into_net(self, param_dict)

    def init_backbone(self, bb_path):
        """Backbone model weights initialization."""
        param_dict = load_mobile_v2_backbone(bb_path)
        info("Backbone param dict:\n {}".format(param_dict))
        load_param_into_net(self.backbone, param_dict)


def load_mobile_v2_backbone(bb_path):
    """load mobile_v2 backbone."""
    param_dict = load_checkpoint(bb_path)
    param_dict_new = {}
    for key, values in param_dict.items():
        if key.startswith('features'):
            if key[9] <= '3' and key[10] == '.':
                param_dict_new['backbone.need_fp1.' + key[9] + '.' + key[11:]] = values
            elif key[9] <= '6' and key[10] == '.':
                param_dict_new['backbone.need_fp2.' + str(int(key[9]) - 4) + '.' + key[11:]] = values
            elif key[9] <= '9' and key[10] == '.':
                param_dict_new['backbone.need_fp3.' + str(int(key[9]) - 7) + '.' + key[11:]] = values
            elif key[9: 11] <= '13':
                param_dict_new['backbone.need_fp3.' + str(int(key[9: 11]) - 7) + '.' + key[12:]] = values
            elif key[9: 11] <= '17':
                param_dict_new['backbone.need_fp4.' + str(int(key[9: 11]) - 14) + '.' + key[12:]] = values
            else:
                continue
    return param_dict_new
