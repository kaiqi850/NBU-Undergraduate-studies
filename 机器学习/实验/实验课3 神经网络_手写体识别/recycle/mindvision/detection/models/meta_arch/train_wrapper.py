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
""" Wrap training process """

import numpy as np
from mindspore import Tensor
from mindspore import nn, context, FixedLossScaleManager
from mindspore.communication import get_group_size
from mindspore.context import ParallelMode
from mindspore.ops import composite as C
from mindspore.ops import functional as F
from mindspore.parallel._auto_parallel_context import auto_parallel_context
from mindspore.train import amp

from mindvision.detection.models.detector.yolo import keep_loss_fp32
from mindvision.engine.class_factory import ClassFactory, ModuleType


@ClassFactory.register(ModuleType.WRAPPER)
class TrainingWrapper(nn.Cell):
    """Training wrapper."""

    def __init__(self, network, optimizer, sens=1.0):
        super(TrainingWrapper, self).__init__(auto_prefix=False)
        self.network = network
        self.network.set_grad()
        self.weights = optimizer.parameters
        self.optimizer = optimizer
        self.grad = C.GradOperation(get_by_list=True, sens_param=True)
        self.sens = Tensor((np.ones((1,)) * sens).astype(np.float32))
        self.reducer_flag = False
        self.grad_reducer = None
        self.parallel_mode = context.get_auto_parallel_context("parallel_mode")
        if self.parallel_mode in [ParallelMode.DATA_PARALLEL, ParallelMode.HYBRID_PARALLEL]:
            self.reducer_flag = True
        if self.reducer_flag:
            mean = context.get_auto_parallel_context("gradients_mean")
            if auto_parallel_context().get_device_num_is_set():
                degree = context.get_auto_parallel_context("device_num")
            else:
                degree = get_group_size()
            self.grad_reducer = nn.DistributedGradReducer(optimizer.parameters, mean, degree)

    def construct(self, *args):
        """Train construct."""
        weights = self.weights
        loss = self.network(*args)
        grads = self.grad(self.network, weights)(*args, self.sens)
        if self.reducer_flag:
            grads = self.grad_reducer(grads)
        return F.depend(loss, self.optimizer(grads))

    def get_network(self):
        """Get network define."""
        is_gpu = context.get_context("device_target") == "GPU"
        if is_gpu:
            loss_scale_value = 1.0
            loss_scale = FixedLossScaleManager(
                loss_scale_value, drop_overflow_update=False
            )
            net = amp.build_train_network(
                self.network, optimizer=self.optimizer,
                loss_scale_manager=loss_scale, level="O2", keep_batchnorm_fp32=False
            )
            keep_loss_fp32(net)
        else:
            net = self
            net.set_train()

        return net


grad_scale = C.MultitypeFuncGraph("grad_scale")
@grad_scale.register("Tensor", "Tensor")
def tensor_grad_scale(scale, grad):
    return grad * P.Reciprocal()(scale)

@ClassFactory.register(ModuleType.WRAPPER)
class TrainingWrapperssd(nn.Cell):
    """
    Encapsulation class of SSD network training.

    Append an optimizer to the training network after that the construct
    function can be called to create the backward graph.

    Args:
        network (Cell): The training network. Note that loss function should have been added.
        optimizer (Optimizer): Optimizer for updating the weights.
        sens (Number): The adjust parameter. Default: 1.0.
        use_global_nrom(bool): Whether apply global norm before optimizer. Default: False
    """

    def __init__(self, network, optimizer, sens=1.0, use_global_norm=True):
        super(TrainingWrapperssd, self).__init__(auto_prefix=False)
        self.network = network
        self.network.set_grad()
        self.weights = ms.ParameterTuple(network.trainable_params())
        self.optimizer = optimizer
        self.grad = C.GradOperation(get_by_list=True, sens_param=True)
        self.sens = sens
        self.reducer_flag = False
        self.grad_reducer = None
        self.use_global_norm = use_global_norm
        self.parallel_mode = context.get_auto_parallel_context("parallel_mode")
        if self.parallel_mode in [ParallelMode.DATA_PARALLEL, ParallelMode.HYBRID_PARALLEL]:
            self.reducer_flag = True
        if self.reducer_flag:
            mean = context.get_auto_parallel_context("gradients_mean")
            if auto_parallel_context().get_device_num_is_set():
                degree = context.get_auto_parallel_context("device_num")
            else:
                degree = get_group_size()
            self.grad_reducer = nn.DistributedGradReducer(optimizer.parameters, mean, degree)
        self.hyper_map = C.HyperMap()

    def construct(self, *args):
        """ssd construct"""
        weights = self.weights
        loss = self.network(*args)
        sens = P.Fill()(P.DType()(loss), P.Shape()(loss), self.sens)
        grads = self.grad(self.network, weights)(*args, sens)
        if self.reducer_flag:
            # apply grad reducer on grads
            grads = self.grad_reducer(grads)
        if self.use_global_norm:
            grads = self.hyper_map(F.partial(grad_scale, F.scalar_to_array(self.sens)), grads)
            grads = C.clip_by_global_norm(grads)
        self.optimizer(grads)
        return loss

    def get_network(self):
        """Get network define."""
        is_gpu = context.get_context("device_target") == "GPU"
        if is_gpu:
            loss_scale_value = 1.0
            loss_scale = FixedLossScaleManager(
                loss_scale_value, drop_overflow_update=False
            )
            net = amp.build_train_network(
                self.network, optimizer=self.optimizer,
                loss_scale_manager=loss_scale, level="O2", keep_batchnorm_fp32=False
            )
            keep_loss_fp32(net)
        else:
            net = self
            net.set_train()

        return net
