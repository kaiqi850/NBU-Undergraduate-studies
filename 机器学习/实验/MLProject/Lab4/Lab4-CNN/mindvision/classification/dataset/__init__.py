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
""" Init dataset """

from . import cifar10, cifar100, mnist, imagenet, fashion_mnist
from .imagenet import *
from .mnist import *
from .cifar10 import *
from .cifar100 import *
from .fashion_mnist import *

__all__ = []
__all__.extend(imagenet.__all__)
__all__.extend(mnist.__all__)
__all__.extend(cifar10.__all__)
__all__.extend(cifar100.__all__)
__all__.extend(fashion_mnist.__all__)
