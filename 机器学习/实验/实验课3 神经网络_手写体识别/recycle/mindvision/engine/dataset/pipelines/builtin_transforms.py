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
"""The module is used to register MindSpore builtin data augment APIs."""

import inspect

import mindspore.dataset.vision.py_transforms as PY
import mindspore.dataset.vision.c_transforms as C

from mindvision.engine.class_factory import ClassFactory, ModuleType


def register_builtin_transforms():
    """ register MindSpore builtin dataset class. """
    for module_name in set(dir(C) + dir(PY)):
        if not module_name.startswith('__'):
            transforms = getattr(C, module_name, None) if getattr(C, module_name, None) else getattr(PY, module_name)
            if inspect.isclass(transforms):
                ClassFactory.register_cls(transforms, ModuleType.PIPELINE)
