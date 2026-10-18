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
"""FasterRcnn feature pyramid network."""

import mindspore.nn as nn
from mindspore.ops import operations as P

from mindvision.engine.class_factory import ClassFactory, ModuleType


@ClassFactory.register(ModuleType.NECK)
class RetinaFPN(nn.Cell):
    """Feature pyramid network cell, usually uses as network neck.

    Applies the convolution on multiple, input feature maps
    and output feature map with same channel size. if required num of
    output larger then num of inputs, add extra maxpooling for further
    downsampling;

    Args:
        in_channels (tuple) - Channel size of input feature maps.
        out_channels (int) - Channel size output.
        num_outs (int) - Num of output features.

    Returns:
        Tuple, with tensors of same channel size.

    Examples:
        neck = FeatPyramidNeck([100,200,300], 50, 4)
        input_data = (normal(0,0.1,(1,c,1280//(4*2**i), 768//(4*2**i)),
                      dtype=np.float32) \
                      for i, c in enumerate(config.fpn_in_channels))
        x = neck(input_data)
    """

    def __init__(self,
                 in_channels,
                 out_channels,
                 num_outs):
        super(RetinaFPN, self).__init__()
        self.num_outs = num_outs

        self.l_conv_5_1 = nn.Conv2d(in_channels[-1], out_channels, kernel_size=1, stride=1, pad_mode='same')
        self.interpolate1 = P.ResizeNearestNeighbor((38, 38))
        self.fpn_conv_5_2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, pad_mode='same')

        self.l_conv_4_1 = nn.Conv2d(in_channels[-2], out_channels, kernel_size=1, stride=1, pad_mode='same')
        self.interpolate2 = P.ResizeNearestNeighbor((75, 75))
        self.fpn_conv_4_2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, pad_mode='same')

        self.l_conv_3_1 = nn.Conv2d(in_channels[-3], out_channels, kernel_size=1, stride=1, pad_mode='same')
        self.fpn_conv_3_2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, pad_mode='same')

        self.fpn_conv_6_0 = nn.Conv2d(in_channels[-1], out_channels, kernel_size=3, stride=2, pad_mode='same')

        self.relu_7_1 = nn.ReLU()
        self.fpn_conv_7_2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=2, pad_mode='same')

    def construct(self, inputs):
        """Construct of FPN."""
        _, inputs_3, inputs_4, inputs_5 = inputs
        outs_5 = self.l_conv_5_1(inputs_5)
        outs_5_upsampled = self.interpolate1(outs_5)
        outs_5 = self.fpn_conv_5_2(outs_5)

        outs_4 = self.l_conv_4_1(inputs_4)
        outs_4 = outs_5_upsampled + outs_4
        outs_4_upsampled = self.interpolate2(outs_4)
        outs_4 = self.fpn_conv_4_2(outs_4)

        outs_3 = self.l_conv_3_1(inputs_3)
        outs_3 = outs_4_upsampled + outs_3
        outs_3 = self.fpn_conv_3_2(outs_3)

        outs_6 = self.fpn_conv_6_0(inputs_5)

        outs_7 = self.relu_7_1(outs_6)
        outs_7 = self.fpn_conv_7_2(outs_7)
        outs = (outs_3, outs_4, outs_5, outs_6, outs_7)
        return outs
