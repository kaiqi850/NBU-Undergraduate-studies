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
""" Yolo detector """

import functools
import math
import numpy as np

import mindspore.nn as nn
import mindspore.common.dtype as mstype
from mindspore.common import initializer as init
from mindspore.common.initializer import Initializer as MeInitializer
from mindspore.train.serialization import load_checkpoint, load_param_into_net

from mindvision.detection.models.meta_arch.one_stage_detector import OneStageDetector
from mindvision.engine.class_factory import ClassFactory, ModuleType
from mindvision.log import info, warning


@ClassFactory.register(ModuleType.DETECTOR)
class YOLOv5(OneStageDetector):
    """ The YOLOv5 detector. """
    def init_weights(self, config):
        """Model weights initialization."""
        default_recurisive_init(self)
        load_yolov5_params(config, self)

    def get_trainable_params(self):
        """Param groups for optimizer."""
        decay_params = []
        no_decay_params = []
        for x in self.trainable_params():
            parameter_name = x.name
            if parameter_name.endswith('.bias'):
                # all bias not using weight decay
                no_decay_params.append(x)
            elif parameter_name.endswith('.gamma'):
                # bn weight bias not using weight decay, be carefully for now x not include BN
                no_decay_params.append(x)
            elif parameter_name.endswith('.beta'):
                # bn weight bias not using weight decay, be carefully for now x not include BN
                no_decay_params.append(x)
            else:
                decay_params.append(x)

        return [{'params': no_decay_params, 'weight_decay': 0.0},
                {'params': decay_params}]


@ClassFactory.register(ModuleType.DETECTOR)
class YOLOv4(OneStageDetector):
    """ The YOLOv4 detector. """

    def init_weights(self, config):
        """Model weights initialization."""
        default_recurisive_init(self)
        load_yolov4_params(config, self)

    def get_trainable_params(self):
        """Param groups for optimizer."""
        decay_params = []
        no_decay_params = []
        for x in self.trainable_params():
            parameter_name = x.name
            if parameter_name.endswith('.bias'):
                # all bias not using weight decay
                no_decay_params.append(x)
            elif parameter_name.endswith('.gamma'):
                # bn weight bias not using weight decay, be carefully for now x not include BN
                no_decay_params.append(x)
            elif parameter_name.endswith('.beta'):
                # bn weight bias not using weight decay, be carefully for now x not include BN
                no_decay_params.append(x)
            else:
                decay_params.append(x)

        return [{'params': no_decay_params, 'weight_decay': 0.0},
                {'params': decay_params}]


@ClassFactory.register(ModuleType.DETECTOR)
class YOLOv3(OneStageDetector):
    """ The YOLOv3 detector. """

    def init_weights(self, config):
        """Model weights initialization."""
        default_recurisive_init(self)
        load_yolov3_params(config, self)

    def get_trainable_params(self):
        """Param groups for optimizer."""
        decay_params = []
        no_decay_params = []
        for x in self.trainable_params():
            parameter_name = x.name
            if parameter_name.endswith('.bias'):
                # all bias not using weight decay
                no_decay_params.append(x)
            elif parameter_name.endswith('.gamma'):
                # bn weight bias not using weight decay, be carefully for now x not include BN
                no_decay_params.append(x)
            elif parameter_name.endswith('.beta'):
                # bn weight bias not using weight decay, be carefully for now x not include BN
                no_decay_params.append(x)
            else:
                decay_params.append(x)

        return [{'params': no_decay_params, 'weight_decay': 0.0}, {'params': decay_params}]


def load_yolov3_backbone(net, ckpt_path):
    """Load darknet53 backbone checkpoint."""
    param_dict = load_checkpoint(ckpt_path)
    net.init_parameters_data()
    load_param_into_net(net, param_dict)

    param_not_load = []
    for _, param in net.parameters_and_names():
        if param.name in param_dict:
            pass
        else:
            param_not_load.append(param.name)
    info("Not loading param is : {}".format(len(param_not_load)))

    return net


def load_yolov3_params(args, network):
    """Load yolov3 darknet parameter from checkpoint."""
    if args.pretrained_backbone:
        network = load_yolov3_backbone(network, args.pretrained_backbone)
        info('Load pre-trained backbone {} into network'.format(args.pretrained_backbone))
    else:
        info('Not load pre-trained backbone, please be careful')

    if args.resume_yolov3:
        param_dict = load_checkpoint(args.resume_yolov3)
        param_dict_new = {}
        for key, values in param_dict.items():
            if key.startswith('Moments.'):
                continue
            elif key.startswith('Yolo_network.'):
                param_dict_new[key[13:]] = values
                info('In resume {}'.format(key))
            else:
                param_dict_new[key] = values
                info('In resume {}'.format(key))

        info('Resume finished')
        load_param_into_net(network, param_dict_new)
        info('Load_model {} success'.format(args.resume_yolov3))


def keep_loss_fp32(network):
    """Keep loss of network with float32."""
    for _, cell in network.cells_and_names():
        if isinstance(cell, (OneStageDetector,)):
            cell.to_float(mstype.float32)


def calculate_gain(nonlinearity, param=None):
    r"""Return the recommended gain value for the given nonlinearity function.
    The values are as follows:

    ================= ====================================================
    nonlinearity      gain
    ================= ====================================================
    Linear / Identity :math:`1`
    Conv{1,2,3}D      :math:`1`
    Sigmoid           :math:`1`
    Tanh              :math:`\frac{5}{3}`
    ReLU              :math:`\sqrt{2}`
    Leaky Relu        :math:`\sqrt{\frac{2}{1 + \text{negative\_slope}^2}}`
    ================= ====================================================

    Args:
        nonlinearity: the non-linear function (`nn.functional` name)
        param: optional parameter for the non-linear function

    Examples:
        >>> gain = nn.init.calculate_gain('leaky_relu', 0.2)  # leaky_relu with negative_slope=0.2
    """
    linear_fns = ['linear', 'conv1d', 'conv2d', 'conv3d', 'conv_transpose1d', 'conv_transpose2d', 'conv_transpose3d']
    if nonlinearity in linear_fns or nonlinearity == 'sigmoid':
        return 1
    if nonlinearity == 'tanh':
        return 5.0 / 3
    if nonlinearity == 'relu':
        return math.sqrt(2.0)
    if nonlinearity == 'leaky_relu':
        if param is None:
            negative_slope = 0.01
        elif not isinstance(param, bool) and isinstance(param, int) or isinstance(param, float):
            # True/False are instances of int, hence check above
            negative_slope = param
        else:
            raise ValueError("negative_slope {} not a valid number".format(param))
        return math.sqrt(2.0 / (1 + negative_slope ** 2))

    raise ValueError("Unsupported nonlinearity {}".format(nonlinearity))


def _assignment(arr, num):
    """Assign the value of 'num' and 'arr'."""
    if arr.shape == ():
        arr = arr.reshape(1)
        arr[:] = num
        arr = arr.reshape(())
    else:
        if isinstance(num, np.ndarray):
            arr[:] = num[:]
        else:
            arr[:] = num
    return arr


def _calculate_correct_fan(array, mode):
    mode = mode.lower()
    valid_modes = ['fan_in', 'fan_out']
    if mode not in valid_modes:
        raise ValueError("Mode {} not supported, please use one of {}".format(mode, valid_modes))

    fan_in, fan_out = _calculate_fan_in_and_fan_out(array)
    return fan_in if mode == 'fan_in' else fan_out


def kaiming_uniform_(arr, a=0.0, mode='fan_in', nonlinearity='leaky_relu'):
    r"""Fills the input `Tensor` with values according to the method
    described in `Delving deep into rectifiers: Surpassing human-level
    performance on ImageNet classification` - He, K. et al. (2015), using a
    uniform distribution. The resulting tensor will have values sampled from
    :math:`\mathcal{U}(-\text{bound}, \text{bound})` where

    .. math::
        \text{bound} = \text{gain} \times \sqrt{\frac{3}{\text{fan\_mode}}}

    Also known as He initialization.

    Args:
        arr: an n-dimensional `Tensor`
        a: the negative slope of the rectifier used after this layer (only
        used with ``'leaky_relu'``)
        mode: either ``'fan_in'`` (default) or ``'fan_out'``. Choosing ``'fan_in'``
            preserves the magnitude of the variance of the weights in the
            forward pass. Choosing ``'fan_out'`` preserves the magnitudes in the
            backwards pass.
        nonlinearity: the non-linear function (`nn.functional` name),
            recommended to use only with ``'relu'`` or ``'leaky_relu'`` (default).

    Examples:
        >>> w = np.empty(3, 5)
        >>> nn.init.kaiming_uniform_(w, mode='fan_in', nonlinearity='relu')
    """
    fan = _calculate_correct_fan(arr, mode)
    gain = calculate_gain(nonlinearity, a)
    std = gain / math.sqrt(fan)
    bound = math.sqrt(3.0) * std  # Calculate uniform bounds from standard deviation
    return np.random.uniform(-bound, bound, arr.shape)


def _calculate_fan_in_and_fan_out(arr):
    """Calculate fan in and fan out."""
    dimensions = len(arr.shape)
    if dimensions < 2:
        raise ValueError("Fan in and fan out can not be computed for array with fewer than 2 dimensions")

    num_input_fmaps = arr.shape[1]
    num_output_fmaps = arr.shape[0]
    receptive_field_size = 1
    if dimensions > 2:
        receptive_field_size = functools.reduce(lambda x, y: x * y, arr.shape[2:])
    fan_in = num_input_fmaps * receptive_field_size
    fan_out = num_output_fmaps * receptive_field_size

    return fan_in, fan_out


class KaimingUniform(MeInitializer):
    """Kaiming uniform initializer."""

    def __init__(self, a=0.0, mode='fan_in', nonlinearity='leaky_relu'):
        super(KaimingUniform, self).__init__()
        self.a = a
        self.mode = mode
        self.nonlinearity = nonlinearity

    def _initialize(self, arr):
        tmp = kaiming_uniform_(arr, self.a, self.mode, self.nonlinearity)
        _assignment(arr, tmp)


def default_recurisive_init(custom_cell):
    """Initialize parameter."""
    a = math.sqrt(5)
    for _, cell in custom_cell.cells_and_names():
        if isinstance(cell, nn.Conv2d):
            # import pdb;pdb.set_trace()
            cell.weight.set_data(
                init.initializer(KaimingUniform(a=a),
                                 cell.weight.shape,
                                 cell.weight.dtype)
            )

            if cell.bias is not None:
                fan_in, _ = _calculate_fan_in_and_fan_out(cell.weight)
                bound = 1 / math.sqrt(fan_in)
                cell.bias.set_data(
                    init.initializer(init.Uniform(bound),
                                     cell.bias.shape,
                                     cell.bias.dtype)
                )

        elif isinstance(cell, nn.Dense):
            cell.weight.set_data(
                init.initializer(KaimingUniform(a=a),
                                 cell.weight.shape,
                                 cell.weight.dtype)
            )
            if cell.bias is not None:
                fan_in, _ = _calculate_fan_in_and_fan_out(cell.weight)
                bound = 1 / math.sqrt(fan_in)
                cell.bias.set_data(
                    init.initializer(init.Uniform(bound),
                                     cell.bias.shape,
                                     cell.bias.dtype)
                )
        elif isinstance(cell, (nn.BatchNorm2d, nn.BatchNorm1d)):
            pass


def load_yolov4_backbone(net, ckpt_path):
    """Load cspdarknet53 backbone checkpoint."""
    param_dict = load_checkpoint(ckpt_path)
    param_dict = {key.split("network.")[-1]: value for key, value in param_dict.items()}
    yolo_backbone_prefix = 'feature_map.backbone'
    darknet_backbone_prefix = 'backbone'
    find_param = []
    not_found_param = []
    net.init_parameters_data()
    for name, cell in net.cells_and_names():
        if name.startswith(yolo_backbone_prefix):
            name = name.replace(yolo_backbone_prefix, darknet_backbone_prefix)
            if isinstance(cell, (nn.Conv2d, nn.Dense)):
                darknet_weight = '{}.weight'.format(name)
                darknet_bias = '{}.bias'.format(name)
                if darknet_weight in param_dict:
                    cell.weight.set_data(param_dict[darknet_weight].data)
                    find_param.append(darknet_weight)
                else:
                    not_found_param.append(darknet_weight)
                if darknet_bias in param_dict:
                    cell.bias.set_data(param_dict[darknet_bias].data)
                    find_param.append(darknet_bias)
                else:
                    not_found_param.append(darknet_bias)
            elif isinstance(cell, (nn.BatchNorm2d, nn.BatchNorm1d)):
                darknet_moving_mean = '{}.moving_mean'.format(name)
                darknet_moving_variance = '{}.moving_variance'.format(name)
                darknet_gamma = '{}.gamma'.format(name)
                darknet_beta = '{}.beta'.format(name)
                if darknet_moving_mean in param_dict:
                    cell.moving_mean.set_data(param_dict[darknet_moving_mean].data)
                    find_param.append(darknet_moving_mean)
                else:
                    not_found_param.append(darknet_moving_mean)
                if darknet_moving_variance in param_dict:
                    cell.moving_variance.set_data(param_dict[darknet_moving_variance].data)
                    find_param.append(darknet_moving_variance)
                else:
                    not_found_param.append(darknet_moving_variance)
                if darknet_gamma in param_dict:
                    cell.gamma.set_data(param_dict[darknet_gamma].data)
                    find_param.append(darknet_gamma)
                else:
                    not_found_param.append(darknet_gamma)
                if darknet_beta in param_dict:
                    cell.beta.set_data(param_dict[darknet_beta].data)
                    find_param.append(darknet_beta)
                else:
                    not_found_param.append(darknet_beta)

    info('================Found_param {}========='.format(len(find_param)))
    info(find_param)
    info('================Not_found_param {}========='.format(len(not_found_param)))
    info(not_found_param)
    info('=====Load {} successfully ====='.format(ckpt_path))

    return net


def load_yolov4_params(args, network):
    """Load yolov4 cspdarknet parameter from checkpoint."""
    if args.pretrained_backbone:
        network = load_yolov4_backbone(network, args.pretrained_backbone)
        info('Load pre-trained backbone {} into network'.format(args.pretrained_backbone))
    else:
        info('Not load pre-trained backbone, please be careful')

    if args.resume_yolov4:
        param_dict = load_checkpoint(args.resume_yolov4)
        param_dict_new = {}
        for key, values in param_dict.items():
            if key.startswith('Moments.'):
                continue
            elif key.startswith('Yolo_network.'):
                param_dict_new[key[13:]] = values
                info('In resume {}'.format(key))
            else:
                param_dict_new[key] = values
                info('In resume {}'.format(key))

        info('Resume finished')
        load_param_into_net(network, param_dict_new)
        info('Load_model {} success'.format(args.resume_yolov4))

    if args.filter_weight:
        if args.pretrained_checkpoint:
            param_dict = load_checkpoint(args.pretrained_checkpoint)
            for key in list(param_dict.keys()):
                if key in args.checkpoint_filter_list:
                    info('Filter {}'.format(key))
                    del param_dict[key]
            load_param_into_net(network, param_dict)
            info('Load_model {} success'.format(args.pretrained_checkpoint))
        else:
            warning('Set filter_weight, but not load pretrained_checkpoint, please be careful')


def load_yolov5_backbone(net, ckpt_path):
    """Load yolov5 backbone checkpoint."""
    param_dict = load_checkpoint(ckpt_path)
    param_dict = {key.split("network.")[-1]: value for key, value in param_dict.items()}
    yolo_backbone_prefix = 'feature_map.backbone'
    darknet_backbone_prefix = 'backbone'
    find_param = []
    not_found_param = []
    net.init_parameters_data()
    for name, cell in net.cells_and_names():
        if name.startswith(yolo_backbone_prefix):
            name = name.replace(yolo_backbone_prefix, darknet_backbone_prefix)
            if isinstance(cell, (nn.Conv2d, nn.Dense)):
                darknet_weight = '{}.weight'.format(name)
                darknet_bias = '{}.bias'.format(name)
                if darknet_weight in param_dict:
                    cell.weight.set_data(param_dict[darknet_weight].data)
                    find_param.append(darknet_weight)
                else:
                    not_found_param.append(darknet_weight)
                if darknet_bias in param_dict:
                    cell.bias.set_data(param_dict[darknet_bias].data)
                    find_param.append(darknet_bias)
                else:
                    not_found_param.append(darknet_bias)
            elif isinstance(cell, (nn.BatchNorm2d, nn.BatchNorm1d)):
                darknet_moving_mean = '{}.moving_mean'.format(name)
                darknet_moving_variance = '{}.moving_variance'.format(name)
                darknet_gamma = '{}.gamma'.format(name)
                darknet_beta = '{}.beta'.format(name)
                if darknet_moving_mean in param_dict:
                    cell.moving_mean.set_data(param_dict[darknet_moving_mean].data)
                    find_param.append(darknet_moving_mean)
                else:
                    not_found_param.append(darknet_moving_mean)
                if darknet_moving_variance in param_dict:
                    cell.moving_variance.set_data(param_dict[darknet_moving_variance].data)
                    find_param.append(darknet_moving_variance)
                else:
                    not_found_param.append(darknet_moving_variance)
                if darknet_gamma in param_dict:
                    cell.gamma.set_data(param_dict[darknet_gamma].data)
                    find_param.append(darknet_gamma)
                else:
                    not_found_param.append(darknet_gamma)
                if darknet_beta in param_dict:
                    cell.beta.set_data(param_dict[darknet_beta].data)
                    find_param.append(darknet_beta)
                else:
                    not_found_param.append(darknet_beta)

    info('================Found_param {}========='.format(len(find_param)))
    info(find_param)
    info('================Not_found_param {}========='.format(len(not_found_param)))
    info(not_found_param)
    info('=====Load {} successfully ====='.format(ckpt_path))

    return net


def load_yolov5_params(args, network):
    """Load yolov5 cspdarknet parameter from checkpoint."""
    if args.pretrained_backbone:
        network = load_yolov5_backbone(network, args.pretrained_backbone)
        info('Load pre-trained backbone {} into network'.format(args.pretrained_backbone))
    else:
        info('Not load pre-trained backbone, please be careful')

    if args.resume_yolov4:
        param_dict = load_checkpoint(args.resume_yolov5)
        param_dict_new = {}
        for key, values in param_dict.items():
            if key.startswith('Moments.'):
                continue
            elif key.startswith('Yolo_network.'):
                param_dict_new[key[13:]] = values
                info('In resume {}'.format(key))
            else:
                param_dict_new[key] = values
                info('In resume {}'.format(key))

        info('Resume finished')
        load_param_into_net(network, param_dict_new)
        info('Load_model {} success'.format(args.resume_yolov4))

    if args.filter_weight:
        if args.pretrained_checkpoint:
            param_dict = load_checkpoint(args.pretrained_checkpoint)
            for key in list(param_dict.keys()):
                if key in args.checkpoint_filter_list:
                    info('Filter {}'.format(key))
                    del param_dict[key]
            load_param_into_net(network, param_dict)
            info('Load_model {} success'.format(args.pretrained_checkpoint))
        else:
            warning('Set filter_weight, but not load pretrained_checkpoint, please be careful')
