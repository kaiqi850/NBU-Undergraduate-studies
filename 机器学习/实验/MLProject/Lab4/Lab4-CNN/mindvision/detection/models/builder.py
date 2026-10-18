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
"""Builder of backbone, head, neck, etc..."""
from mindvision.engine.class_factory import ClassFactory, ModuleType


def build_backbone(cfg):
    """Build backbone."""
    return ClassFactory.get_instance_from_cfg(cfg, ModuleType.BACKBONE)


def build_head(cfg):
    """Build head."""
    return ClassFactory.get_instance_from_cfg(cfg, ModuleType.HEAD)


def build_neck(cfg):
    """Build neck."""
    return ClassFactory.get_instance_from_cfg(cfg, ModuleType.NECK)


def build_anchor(cfg):
    """Build anchor."""
    return ClassFactory.get_instance_from_cfg(cfg, ModuleType.ANCHOR_GENERATOR)


def build_detector(cfg):
    """Build detector."""
    return ClassFactory.get_instance_from_cfg(cfg, ModuleType.DETECTOR)


def build_train_wrapper(cfg, default_args=None):
    """Build train wrapper."""
    return ClassFactory.get_instance_from_cfg(cfg, ModuleType.WRAPPER, default_args)


def build_detection_engine(cfg):
    """Build detector."""
    return ClassFactory.get_instance_from_cfg(cfg, ModuleType.DETECTION_ENGINE)
