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
"""Builder of learning rate schedule."""

import inspect

import mindspore as ms

from mindvision.engine.class_factory import ClassFactory, ModuleType


def build_lr_schedule(cfg, default_args=None):
    lr_schedule = ClassFactory.get_instance_from_cfg(
        cfg, ModuleType.LR_SCHEDULE, default_args)
    return lr_schedule


def register_lr_schedule():
    """Register learning rate schedule from in engine. TODO: LR_SCHEDULE using mindspore buildin. """
    for module_name in dir(ms.nn):
        if not module_name.startswith('__'):
            lr_schedule = getattr(ms.nn, module_name)
            if inspect.isfunction(lr_schedule):
                ClassFactory.register_cls(lr_schedule, ModuleType.LR_SCHEDULE)
