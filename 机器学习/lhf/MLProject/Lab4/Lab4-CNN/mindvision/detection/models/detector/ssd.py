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
"""SSD"""
from mindspore.train.serialization import load_checkpoint, load_param_into_net

from models.meta_arch.one_stage_detector import OneStageDetector

from mindvision.common.utils.class_factory import ClassFactory, ModuleType
from mindvision.common.log import info


@ClassFactory.register(ModuleType.DETECTOR)
class SSD(OneStageDetector):
    """
    SSD detection module
    """

    def init_weights(self, config):
        """Model weights initialization."""
        ckpt_path = config.pretrained_checkpoint
        if ckpt_path and ckpt_path != "":
            param_dict = load_checkpoint(ckpt_path)
            info("param dict:\n {}".format(param_dict))
            load_param_into_net(self, param_dict)

    def init_backbone(self, bb_path):
        """Backbone model weights initialization."""
        param_dict_ssd = load_checkpoint(bb_path)
        param_dict_new = {}
        for name in self.parameters_and_names():
            if name.startswith('backbone.'):
                for key, values in param_dict_ssd.items():
                    if name[9:] == key:
                        param_dict_new[name] = values
                    else:
                        continue

        info("Backbone param dict:\n {}".format(param_dict_new))
        load_param_into_net(self.backbone, param_dict_new)
