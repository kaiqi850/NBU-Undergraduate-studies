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
"""FasterRCNN"""
from mindspore.train.serialization import load_checkpoint, load_param_into_net

from mindvision.detection.models.meta_arch.two_stage_detector import TwoStageDetector
from mindvision.engine.class_factory import ClassFactory, ModuleType
from mindvision.log import info


@ClassFactory.register(ModuleType.DETECTOR)
class FasterRCNN(TwoStageDetector):
    """
    FasterRCNN detection module
    """

    def init_weights(self, ckpt_path):
        """Full model weights initialization."""
        param_dict = load_checkpoint(ckpt_path)
        info("Full Network param dict:\n {}".format(param_dict))
        load_param_into_net(self, param_dict)

    def init_backbone(self, bb_path):
        """Backbone model weights initialization."""
        param_dict = load_checkpoint(bb_path)
        info("Backbone param dict:\n {}".format(param_dict))
        load_param_into_net(self.backbone, param_dict)
