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
"""ResNet Full X."""

import math
import numpy as np

import mindspore.nn as nn
from mindspore.common.tensor import Tensor
import mindspore.common.dtype as mstype
from mindspore.ops import operations as P
from mindspore.common.initializer import Initializer as MeInitializer


class GlobalAvgPooling(nn.Cell):
    """
    Global average pooling feature map.
    """

    def __init__(self):
        super(GlobalAvgPooling, self).__init__()
        self.mean = P.ReduceMean(False)

    def construct(self, x):
        """GlobalAvgPooling construct."""
        x = self.mean(x, (2, 3))
        return x


class SEBlock(nn.Cell):
    """
    Squeeze and excitation block.

    Args:
        channel (int): number of feature maps.
        reduction (int): weight.
    """

    def __init__(self, channel, reduction=16):
        super(SEBlock, self).__init__()

        self.avg_pool = GlobalAvgPooling()
        self.fc1 = nn.Dense(channel, channel // reduction)
        self.relu = P.ReLU()
        self.fc2 = nn.Dense(channel // reduction, channel)
        self.sigmoid = P.Sigmoid()
        self.reshape = P.Reshape()
        self.shape = P.Shape()
        self.cast = P.Cast()

    def construct(self, x):
        """SEBlock construct."""
        b, c = self.shape(x)
        y = self.avg_pool(x)

        y = self.reshape(y, (b, c))
        y = self.fc1(y)
        y = self.relu(y)
        y = self.fc2(y)
        y = self.sigmoid(y)
        y = self.reshape(y, (b, c, 1, 1))
        return x * y


class GroupConv(nn.Cell):
    """
    Group convolution operation.

    Args:
        in_channels (int): Input channels of feature map.
        out_channels (int): Output channels of feature map.
        kernel_size (int): Size of convolution kernel.
        stride (int): Stride size for the group convolution layer.

    Returns:
        tensor, output tensor.
    """

    def __init__(self, in_channels, out_channels, kernel_size, stride,
                 pad_mode="pad", pad=0, groups=1, has_bias=False):
        super(GroupConv, self).__init__()
        assert in_channels % groups == 0 and out_channels % groups == 0
        self.groups = groups
        self.convs = nn.CellList()
        self.op_split = P.Split(axis=1, output_num=self.groups)
        self.op_concat = P.Concat(axis=1)
        self.cast = P.Cast()
        for _ in range(groups):
            self.convs.append(nn.Conv2d(in_channels // groups, out_channels // groups,
                                        kernel_size=kernel_size, stride=stride,
                                        has_bias=has_bias, padding=pad,
                                        pad_mode=pad_mode, group=1))

    def construct(self, x):
        """Group convolution operation construct."""
        features = self.op_split(x)
        outputs = ()
        for i in range(self.groups):
            outputs = outputs + (self.convs[i](self.cast(features[i], mstype.float32)),)
        out = self.op_concat(outputs)
        return out


def custom_conv(in_channel, out_channel, kernel_size=3, stride=1, padding=3,
                has_bias=False, pad_mode='pad', activation="relu", depth=50):
    weight_shape = (out_channel, in_channel, kernel_size, kernel_size)
    weight = Tensor(kaiming_normal(weight_shape, mode="fan_out", nonlinearity=activation))
    if depth == 152:
        weight = init_weight_variable(weight_shape)
    return nn.Conv2d(in_channel, out_channel,
                     kernel_size=kernel_size, stride=stride,
                     padding=padding, pad_mode=pad_mode,
                     weight_init=weight, has_bias=has_bias)


def custom_bn(channel, momentum=0.1, norm_layer=None, affine=True, use_batch_statistics=True, default_bn=False):
    """BatchNormalize operation construct."""
    dtype = np.float32
    gamma_init = Tensor(np.array(np.ones(channel)).astype(dtype))
    beta_init = Tensor(np.array(np.ones(channel) * 0).astype(dtype))
    moving_mean_init = Tensor(np.array(np.ones(channel) * 0).astype(dtype))
    moving_var_init = Tensor(np.array(np.ones(channel)).astype(dtype))
    normalization_layer = _get_normal_layer(norm_layer)
    if default_bn:
        return normalization_layer(channel, eps=1e-5, momentum=momentum, affine=affine,
                                   gamma_init=gamma_init, beta_init=beta_init,
                                   moving_mean_init=moving_mean_init,
                                   moving_var_init=moving_var_init)
    return normalization_layer(channel, eps=1e-5, momentum=momentum, affine=affine,
                               gamma_init=gamma_init, beta_init=beta_init,
                               moving_mean_init=moving_mean_init,
                               moving_var_init=moving_var_init,
                               use_batch_statistics=use_batch_statistics)


def custom_down_sample(in_channel, out_channel, stride=1, momentum=0.1,
                       affine=False, use_batch_statistics=False,
                       norm_layer=None, pad_mode='pad',
                       activation="relu", depth=50, default_bn=False):
    """
    down-sample for ResNet.

    Args:
        in_channel (int): Input channels.
        out_channel (int): Output channels.
        stride (int): Stride size for the 1*1 convolutional layer.
        momentum (float): bn momentum, default is 0.1.
        affine (bool): Default is False.
        use_batch_statistics (bool): Default is False.
        norm_layer (str): Normalization layer, default is None.
        pad_mode (str): Pad mode, default is 'pad'.
        activation (str): Activation function, default is "relu".
        depth (int): Network depth, default is 50.

    Returns:
        Tensor, output tensor.
    """
    conv_down_sample = custom_conv(in_channel, out_channel,
                                   kernel_size=1, stride=stride,
                                   padding=0, pad_mode=pad_mode,
                                   activation=activation, depth=depth)
    bn_down_sample = custom_bn(out_channel, affine=affine,
                               momentum=momentum, norm_layer=norm_layer,
                               use_batch_statistics=use_batch_statistics,
                               default_bn=default_bn)
    if use_batch_statistics:
        bn_down_sample = bn_down_sample.set_train()
    if not affine:
        conv_down_sample.weight.requires_grad = False

    return nn.SequentialCell([conv_down_sample, bn_down_sample])


def _get_normal_layer(norm_layer='BN2d'):
    """Get Normalization layer."""
    norm_layers = {'BN2d': nn.BatchNorm2d,
                   'GN': nn.GroupNorm,
                   'IN': nn.InstanceNorm2d,
                   'LN': nn.LayerNorm,
                   'GBN': nn.GlobalBatchNorm
                   }
    if norm_layer not in norm_layers:
        raise ValueError("Unsupported normalization layer {}".format(norm_layer))

    return norm_layers.get(norm_layer)


def _calculate_gain(nonlinearity, param=None):
    """Calculate gain"""
    linear_fns = ['linear', 'conv1d', 'conv2d', 'conv3d', 'conv_transpose1d', 'conv_transpose2d', 'conv_transpose3d']
    gain = 0
    if nonlinearity in linear_fns or nonlinearity == 'sigmoid':
        gain = 1
    elif nonlinearity == 'tanh':
        gain = 5.0 / 3
    elif nonlinearity == 'relu':
        gain = math.sqrt(2.0)
    elif nonlinearity == 'leaky_relu':
        if param is None:
            neg_slope = 0.01
        elif not isinstance(param, bool) and isinstance(param, int) or isinstance(param, float):
            neg_slope = param
        else:
            raise ValueError("Negative Slope {} not a valid number.".format(param))
        gain = math.sqrt(2.0 / (1 + neg_slope ** 2))
    else:
        raise ValueError("Unsupported nonlinearity {}.".format(nonlinearity))

    return gain


def _calculate_fan_in_and_fan_out(tensor):
    """Calculate fan_in and fan_out."""
    dimensions = len(tensor)
    if dimensions < 2:
        raise ValueError("Fan in and fan out can not be computed for tensor with fewer than 2 dimensions.")
    if dimensions == 2:  # Linear
        fan_in = tensor[1]
        fan_out = tensor[0]
    else:
        num_input_fmaps = tensor[1]
        num_output_fmaps = tensor[0]
        receptive_field_size = 1
        if dimensions > 2:
            receptive_field_size = tensor[2] * tensor[3]
        fan_in = num_input_fmaps * receptive_field_size
        fan_out = num_output_fmaps * receptive_field_size
    return fan_in, fan_out


def _calculate_correct_fan(tensor, mode):
    """Calculate correct fan."""
    mode = mode.lower()
    valid_modes = ['fan_in', 'fan_out']
    if mode not in valid_modes:
        raise ValueError("Unsupported mode {}, please use one of {}.".format(mode, valid_modes))
    fan_in, fan_out = _calculate_fan_in_and_fan_out(tensor)
    return fan_in if mode == 'fan_in' else fan_out


def kaiming_normal(inputs_shape, a=0, mode='fan_in', nonlinearity='leaky_relu'):
    """Init weight of kaiming normol."""
    fan = _calculate_correct_fan(inputs_shape, mode)
    gain = _calculate_gain(nonlinearity, a)
    std = gain / math.sqrt(fan)
    return np.random.normal(0, std, size=inputs_shape).astype(np.float32)


def kaiming_uniform(inputs_shape, a=0., mode='fan_in', nonlinearity='leaky_relu'):
    """Init weight of kaiming uniform."""
    fan = _calculate_correct_fan(inputs_shape, mode)
    gain = _calculate_gain(nonlinearity, a)
    std = gain / math.sqrt(fan)
    bound = math.sqrt(3.0) * std  # Calculate uniform bounds from standard deviation
    return np.random.uniform(-bound, bound, size=inputs_shape).astype(np.float32)


def init_weight_variable(shape, factor=0.01):
    """Init weight variable."""
    init_value = np.random.randn(*shape).astype(np.float32) * factor
    return Tensor(init_value)


def network_convert_type(network, cfg):
    """convert network type"""
    mstype_type_dict = {'float16': mstype.float16,
                        'float32': mstype.float32,
                        'float64': mstype.float64}
    if cfg is None:
        network.to_float(mstype.float16)
    else:
        for k, v in cfg.items():
            if k == 'backbone':
                network.backbone.to_float(mstype_type_dict[v])
            elif k == 'neck':
                network.neck.to_float(mstype_type_dict[v])
            elif k == 'bbox_head':
                network.bbox_head.to_float(mstype_type_dict[v])


def assignment(arr, num):
    """Assign the value of `num` to `arr`."""
    if arr.shape == ():
        arr = arr.reshape((1))
        arr[:] = num
        arr = arr.reshape(())
    else:
        if isinstance(num, np.ndarray):
            arr[:] = num[:]
        else:
            arr[:] = num
    return arr


class KaimingNormal(MeInitializer):
    """
    KaimingNormal
    """

    def __init__(self, a=0, mode='fan_in', nonlinearity='leaky_relu'):
        super(KaimingNormal, self).__init__()
        self.a = a
        self.mode = mode
        self.nonlinearity = nonlinearity

    def _initialize(self, arr):
        inputs_shape = arr.shape
        tmp = kaiming_normal(inputs_shape, self.a, self.mode, self.nonlinearity)
        assignment(arr, tmp)
