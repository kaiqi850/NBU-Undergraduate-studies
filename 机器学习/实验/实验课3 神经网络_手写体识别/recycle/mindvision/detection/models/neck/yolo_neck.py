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
""" YOLO neck implement"""

from mindspore import nn
from mindspore.ops import operations as P

from mindvision.engine.class_factory import ClassFactory, ModuleType


def _conv_bn_leaky_relu(in_channel,
                        out_channel,
                        ksize,
                        stride=1,
                        padding=0,
                        dilation=1,
                        alpha=0.1,
                        momentum=0.9,
                        eps=1e-5,
                        pad_mode="same"):
    """Get a conv2d batch norm and leaky relu layer"""
    return nn.SequentialCell(
        [nn.Conv2d(in_channel,
                   out_channel,
                   kernel_size=ksize,
                   stride=stride,
                   padding=padding,
                   dilation=dilation,
                   pad_mode=pad_mode),
         nn.BatchNorm2d(out_channel, momentum=momentum, eps=eps),
         nn.LeakyReLU(alpha)]
    )


class YoloBlock(nn.Cell):
    """YoloBlock for YOLO.

    Args:
        in_channels: Integer. Input channel.
        out_chs: Integer. Middle channel.
        out_channels: Integer. Output channel.

    Returns:
        Tuple, tuple of output tensor,(f1,f2,f3).

    Examples:
        YoloBlock(1024, 512, 255)

    """

    def __init__(self, in_channels, out_chs, out_channels):
        super(YoloBlock, self).__init__()
        out_chs_2 = out_chs * 2

        self.conv0 = _conv_bn_leaky_relu(in_channels, out_chs, ksize=1)
        self.conv1 = _conv_bn_leaky_relu(out_chs, out_chs_2, ksize=3)

        self.conv2 = _conv_bn_leaky_relu(out_chs_2, out_chs, ksize=1)
        self.conv3 = _conv_bn_leaky_relu(out_chs, out_chs_2, ksize=3)

        self.conv4 = _conv_bn_leaky_relu(out_chs_2, out_chs, ksize=1)
        self.conv5 = _conv_bn_leaky_relu(out_chs, out_chs_2, ksize=3)

        self.conv6 = nn.Conv2d(out_chs_2, out_channels, kernel_size=1,
                               stride=1, has_bias=True)

    def construct(self, x):
        """Construct of YoloBlock."""
        c1 = self.conv0(x)
        c2 = self.conv1(c1)

        c3 = self.conv2(c2)
        c4 = self.conv3(c3)

        c5 = self.conv4(c4)
        c6 = self.conv5(c5)

        out = self.conv6(c6)
        return c5, out


@ClassFactory.register(ModuleType.NECK)
class YOLOv3Neck(nn.Cell):
    """The neck of YOLOv3.

    Note:
         backbone = darknet53

     Args:
         backbone_shape: List. Darknet output channels shape.
         out_channel: Integer. Output channel.

     Returns:
         Tensor, output tensor.

     Examples:
         YOLOv3Neck(backbone_shape=[64, 128, 256, 512, 1024]
                backbone=darknet53(),
                out_channel=255)
    """

    def __init__(self, backbone_shape, out_channel):
        super(YOLOv3Neck, self).__init__()
        self.out_channel = out_channel
        self.back_block0 = YoloBlock(backbone_shape[-1],
                                     out_chs=backbone_shape[-2],
                                     out_channels=out_channel)

        self.conv1 = _conv_bn_leaky_relu(in_channel=backbone_shape[-2],
                                         out_channel=backbone_shape[-2] // 2,
                                         ksize=1)
        self.back_block1 = YoloBlock(
            in_channels=backbone_shape[-2] + backbone_shape[-3],
            out_chs=backbone_shape[-3],
            out_channels=out_channel
        )

        self.conv2 = _conv_bn_leaky_relu(in_channel=backbone_shape[-3],
                                         out_channel=backbone_shape[-3] // 2,
                                         ksize=1)
        self.back_block2 = YoloBlock(
            in_channels=backbone_shape[-3] + backbone_shape[-4],
            out_chs=backbone_shape[-4],
            out_channels=out_channel
        )
        self.concat = P.Concat(axis=1)

    def construct(self, x):
        """Construct of YOLOv3Neck."""
        feature_map3, feature_map2, feature_map1 = x[2], x[1], x[0]
        img_height = P.Shape()(feature_map1)[2] * 8
        img_width = P.Shape()(feature_map1)[3] * 8

        con1, big_object_output = self.back_block0(feature_map3)

        con1 = self.conv1(con1)
        ups1 = P.ResizeNearestNeighbor(
            (img_height // 16, img_width // 16))(con1)
        con1 = self.concat((ups1, feature_map2))
        con2, medium_object_output = self.back_block1(con1)

        con2 = self.conv2(con2)
        ups2 = P.ResizeNearestNeighbor((img_height // 8, img_width // 8))(con2)
        con3 = self.concat((ups2, feature_map1))
        _, small_object_output = self.back_block2(con3)

        return big_object_output, medium_object_output, small_object_output


@ClassFactory.register(ModuleType.NECK)
class YOLOv4Neck(nn.Cell):
    """The neck of yolov4

     Note:
         backbone = CspDarkNet53

     Args:
         backbone_shape: List. Darknet output channels shape.
         backbone: Cell. Backbone Network.
         out_channel: Integer. Output channel.

     Returns:
         Tensor, output tensor.

     Examples:
         YOLOv4(feature_shape=[1,3,416,416],
                backbone_shape=[64, 128, 256, 512, 1024]
                backbone=CspDarkNet53(),
                out_channel=255)
     """

    def __init__(self, backbone_shape, out_channel):
        super(YOLOv4Neck, self).__init__()
        self.out_channel = out_channel

        self.conv1 = _conv_bn_leaky_relu(1024, 512, ksize=1)
        self.conv2 = _conv_bn_leaky_relu(512, 1024, ksize=3)
        self.conv3 = _conv_bn_leaky_relu(1024, 512, ksize=1)

        self.maxpool1 = nn.MaxPool2d(kernel_size=5, stride=1, pad_mode='same')
        self.maxpool2 = nn.MaxPool2d(kernel_size=9, stride=1, pad_mode='same')
        self.maxpool3 = nn.MaxPool2d(kernel_size=13, stride=1, pad_mode='same')
        self.conv4 = _conv_bn_leaky_relu(2048, 512, ksize=1)

        self.conv5 = _conv_bn_leaky_relu(512, 1024, ksize=3)
        self.conv6 = _conv_bn_leaky_relu(1024, 512, ksize=1)
        self.conv7 = _conv_bn_leaky_relu(512, 256, ksize=1)

        self.conv8 = _conv_bn_leaky_relu(512, 256, ksize=1)
        self.back_block0 = YoloBlock(backbone_shape[-2],
                                     out_chs=backbone_shape[-3],
                                     out_channels=out_channel)

        self.conv9 = _conv_bn_leaky_relu(256, 128, ksize=1)
        self.conv10 = _conv_bn_leaky_relu(256, 128, ksize=1)
        self.conv11 = _conv_bn_leaky_relu(128, 256, ksize=3, stride=2)
        self.conv12 = _conv_bn_leaky_relu(256, 512, ksize=3, stride=2)

        self.back_block1 = YoloBlock(backbone_shape[-3],
                                     out_chs=backbone_shape[-4],
                                     out_channels=out_channel)
        self.back_block2 = YoloBlock(backbone_shape[-2],
                                     out_chs=backbone_shape[-3],
                                     out_channels=out_channel)
        self.back_block3 = YoloBlock(backbone_shape[-1],
                                     out_chs=backbone_shape[-2],
                                     out_channels=out_channel)

        self.concat = P.Concat(axis=1)

    def construct(self, x):
        """
        x is the feature maps (f3, f2, f1)
        feature_map1 is (batch_size, backbone_shape[2], h/8, w/8)
        feature_map2 is (batch_size, backbone_shape[3], h/16, w/16)
        feature_map3 is (batch_size, backbone_shape[4], h/32, w/32)
        """
        feature_map3, feature_map2, feature_map1 = x[2], x[1], x[0]

        img_height = P.Shape()(feature_map1)[2] * 8
        img_width = P.Shape()(feature_map1)[3] * 8

        con1 = self.conv1(feature_map3)
        con2 = self.conv2(con1)
        con3 = self.conv3(con2)

        m1 = self.maxpool1(con3)
        m2 = self.maxpool2(con3)
        m3 = self.maxpool3(con3)
        spp = self.concat((m3, m2, m1, con3))
        con4 = self.conv4(spp)

        con5 = self.conv5(con4)
        con6 = self.conv6(con5)
        con7 = self.conv7(con6)

        ups1 = P.ResizeNearestNeighbor((img_height // 16, img_width // 16))(con7)
        con8 = self.conv8(feature_map2)
        con9 = self.concat((ups1, con8))
        con10, _ = self.back_block0(con9)
        con11 = self.conv9(con10)
        ups2 = P.ResizeNearestNeighbor((img_height // 8, img_width // 8))(con11)
        con12 = self.conv10(feature_map1)
        con13 = self.concat((ups2, con12))
        con14, small_object_output = self.back_block1(con13)

        con15 = self.conv11(con14)
        con16 = self.concat((con15, con10))
        con17, medium_object_output = self.back_block2(con16)

        con18 = self.conv12(con17)
        con19 = self.concat((con18, con6))
        _, big_object_output = self.back_block3(con19)
        return big_object_output, medium_object_output, small_object_output


def autopad(k, p=None):
    """
    Pad to 'same'
    """
    if p is None:
        p = k // 2 if isinstance(k, int) else [x // 2 for x in k]
    return p


class SiLU(nn.Cell):
    def __init__(self):
        super(SiLU, self).__init__()
        self.sigmoid = P.Sigmoid()

    def construct(self, x):
        return x * self.sigmoid(x)


class Conv(nn.Cell):
    """
    Standard convolution
    """
    def __init__(self, c1, c2, k=1, s=1, p=None,
                 momentum=0.97,
                 eps=1e-3,
                 act=True):
        super(Conv, self).__init__()
        self.padding = autopad(k, p)
        self.pad_mode = None
        if self.padding == 0:
            self.pad_mode = 'same'
        elif self.padding == 1:
            self.pad_mode = 'pad'
        self.conv = nn.Conv2d(c1, c2, k, s, padding=self.padding, pad_mode=self.pad_mode, has_bias=False)
        self.bn = nn.BatchNorm2d(c2, momentum=momentum, eps=eps)
        self.act = SiLU() if act is True else (act if isinstance(act, nn.Cell) else P.Identity())

    def construct(self, x):
        return self.act(self.bn(self.conv(x)))


class Bottleneck(nn.Cell):
    """
    Standard bottleneck
    """
    def __init__(self, c1, c2, shortcut=True, e=0.5):
        super(Bottleneck, self).__init__()
        c_ = int(c2 * e)
        self.cv1 = Conv(c1, c_, 1, 1)
        self.cv2 = Conv(c_, c2, 3, 1)
        self.add = shortcut and c1 == c2

    def construct(self, x):
        return x + self.cv2(self.cv1(x)) if self.add else self.cv2(self.cv1(x))


class C3(nn.Cell):
    """
    CSP Bottleneck with 3 convolutions
    """

    def __init__(self, c1, c2, n=1, shortcut=True, e=0.5):
        super(C3, self).__init__()
        c_ = int(c2 * e)
        self.cv1 = Conv(c1, c_, 1, 1)
        self.cv2 = Conv(c1, c_, 1, 1)
        self.cv3 = Conv(2 * c_, c2, 1)
        self.m = nn.SequentialCell([Bottleneck(c_, c_, shortcut, e=1.0) for _ in range(n)])
        self.concat = P.Concat(1)

    def construct(self, x):
        y1 = self.m(self.cv1(x))
        y2 = self.cv2(x)
        concat2 = self.concat((y1, y2))
        return self.cv3(concat2)


class YOLOv5Block(nn.Cell):
    """
    YoloBlock for YOLOv5.

    Args:
        in_channels: Integer. Input channel.
        out_channels: Integer. Output channel.

    Returns:
        Tuple, tuple of output tensor,(f1,f2,f3).

    Examples:
        YoloBlock(12, 255)

    """

    def __init__(self, in_channels, out_channels):
        super(YOLOv5Block, self).__init__()

        self.cv = nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=1, has_bias=True)

    def construct(self, x):
        """construct method"""

        out = self.cv(x)
        return out


@ClassFactory.register(ModuleType.NECK)
class YOLOv5Neck(nn.Cell):
    """The neck of yolov5

     Note:
         backbone = YOLOv5Backbone

     Args:
         backbone_shape: List. YOLOv5Backbone output channels shape.
         backbone: Cell. Backbone Network.
         out_channel: Integer. Output channel.

     Returns:
         Tensor, output tensor.

     Examples:
         YOLOv5(feature_shape=[1,3,416,416],
                backbone_shape=[64, 128, 256, 512, 1024]
                backbone=CspDarkNet53(),
                out_channel=255)
     """

    def __init__(self, backbone_shape, out_channel):
        super(YOLOv5Neck, self).__init__()
        self.out_channel = out_channel
        self.backbone_shape = backbone_shape

        self.conv1 = Conv(512, 256, k=1, s=1)
        self._c31 = C3(512, 256, n=1, shortcut=False)
        self.conv2 = Conv(256, 128, k=1, s=1)
        self._c32 = C3(256, 128, n=1, shortcut=False)
        self.conv3 = Conv(128, 128, k=3, s=2)
        self._c33 = C3(256, 256, n=1, shortcut=False)
        self.conv4 = Conv(256, 256, k=3, s=2)
        self._c34 = C3(512, 512, n=1, shortcut=False)

        self.backblock1 = YOLOv5Block(128, 255)
        self.backblock2 = YOLOv5Block(256, 255)
        self.backblock3 = YOLOv5Block(512, 255)

        self.concat = P.Concat(axis=1)

    def construct(self, x):
        """
        x is the feature maps (f3, f2, f1)
        feature_map1 is (batch_size, backbone_shape[2], h/8, w/8)
        feature_map2 is (batch_size, backbone_shape[3], h/16, w/16)
        feature_map3 is (batch_size, backbone_shape[4], h/32, w/32)
        """
        feature_map1, feature_map2, feature_map3 = x[0], x[1], x[2]

        cv1 = self.conv1(feature_map3)
        ups1 = P.ResizeNearestNeighbor((40, 40))(cv1)
        concat1 = self.concat((ups1, feature_map2))
        bcsp1 = self._c31(concat1)
        cv2 = self.conv2(bcsp1)
        ups2 = P.ResizeNearestNeighbor((80, 80))(cv2)
        concat2 = self.concat((ups2, feature_map1))
        bcsp2 = self._c32(concat2)
        cv3 = self.conv3(bcsp2)

        concat3 = self.concat((cv3, cv2))
        bcsp3 = self._c33(concat3)
        cv4 = self.conv4(bcsp3)
        concat4 = self.concat((cv4, cv1))
        bcsp4 = self._c34(concat4)
        small_object_output = self.backblock1(bcsp2)
        medium_object_output = self.backblock2(bcsp3)
        big_object_output = self.backblock3(bcsp4)
        return big_object_output, medium_object_output, small_object_output
