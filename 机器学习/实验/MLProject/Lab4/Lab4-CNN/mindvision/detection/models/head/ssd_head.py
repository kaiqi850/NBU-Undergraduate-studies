"""head for Ssd"""
import mindspore.common.dtype as mstype
import mindspore.nn as nn
from mindspore import Tensor
from mindspore.ops import functional as F
from mindspore.ops import operations as P

from mindvision.common.utils.class_factory import ClassFactory, ModuleType
from mindvision.detection.internals.anchor.generate_Default_box_ssd import default_boxes

def _make_divisible(v, divisor, min_value=None):
    """nsures that all layers have a channel number that is divisible by 8."""
    if min_value is None:
        min_value = divisor
    new_v = max(min_value, int(v + divisor / 2) // divisor * divisor)
    # Make sure that round down does not go down by more than 10%.
    if new_v < 0.9 * v:
        new_v += divisor
    return new_v


def _conv2d(in_channel, out_channel, kernel_size=3, stride=1, pad_mod='same'):
    return nn.Conv2d(in_channel, out_channel, kernel_size=kernel_size, stride=stride,
                     padding=0, pad_mode=pad_mod, has_bias=True)


def _bn(channel):
    return nn.BatchNorm2d(channel, eps=1e-3, momentum=0.97,
                          gamma_init=1, beta_init=0, moving_mean_init=0, moving_var_init=1)


class FlattenConcat(nn.Cell):
    """
    Concatenate predictions into a single tensor.

    Args:
        config (dict): The default config of SSD.

    Returns:
        Tensor, flatten predictions.
    """

    def __init__(self, config):
        super(FlattenConcat, self).__init__()
        self.num_ssd_boxes = config.num_ssd_boxes
        self.concat = P.Concat(axis=1)
        self.transpose = P.Transpose()

    def construct(self, inputs):
        output = ()
        batch_size = F.shape(inputs[0])[0]
        for x in inputs:
            x = self.transpose(x, (0, 2, 3, 1))
            output += (F.reshape(x, (batch_size, -1)),)
        res = self.concat(output)
        return F.reshape(res, (batch_size, self.num_ssd_boxes, -1))


class SigmoidFocalClassificationLoss(nn.Cell):
    """"
    Sigmoid focal-loss for classification.

    Args:
        gamma (float): Hyper-parameter to balance the easy and hard examples. Default: 2.0
        alpha (float): Hyper-parameter to balance the positive and negative example. Default: 0.25

    Returns:
        Tensor, the focal loss.
    """

    def __init__(self, gamma=2.0, alpha=0.25):
        super(SigmoidFocalClassificationLoss, self).__init__()
        self.sigmiod_cross_entropy = P.SigmoidCrossEntropyWithLogits()
        self.sigmoid = P.Sigmoid()
        self.pow = P.Pow()
        self.onehot = P.OneHot()
        self.on_value = Tensor(1.0, mstype.float32)
        self.off_value = Tensor(0.0, mstype.float32)
        self.gamma = gamma
        self.alpha = alpha

    def construct(self, logits, label):
        label = self.onehot(label, F.shape(logits)[-1], self.on_value, self.off_value)
        sigmiod_cross_entropy = self.sigmiod_cross_entropy(logits, label)
        sigmoid = self.sigmoid(logits)
        label = F.cast(label, mstype.float32)
        p_t = label * sigmoid + (1 - label) * (1 - sigmoid)
        modulating_factor = self.pow(1 - p_t, self.gamma)
        alpha_weight_factor = label * self.alpha + (1 - label) * (1 - self.alpha)
        focal_loss = modulating_factor * alpha_weight_factor * sigmiod_cross_entropy
        return focal_loss


class SsdInferWithDecoder(nn.Cell):
    """
    SSD Infer wrapper to decode the bbox locations.

    Args:
        network (Cell): the origin ssd infer network without bbox decoder.
        default_boxes (Tensor): the default_boxes from anchor generator
        config (dict): ssd config
    Returns:
        Tensor, the locations for bbox after decoder representing (y0,x0,y1,x1)
        Tensor, the prediction labels.

    """

    def __init__(self, network, default_boxes_infer, config):
        super(SsdInferWithDecoder, self).__init__()
        self.network = network
        self.default_boxes = default_boxes_infer
        self.prior_scaling_xy = config.prior_scaling[0]
        self.prior_scaling_wh = config.prior_scaling[1]

    def construct(self, x):
        """forward pass"""
        pred_loc, pred_label = self.network(x)

        default_bbox_xy = self.default_boxes[..., :2]
        default_bbox_wh = self.default_boxes[..., 2:]
        pred_xy = pred_loc[..., :2] * self.prior_scaling_xy * default_bbox_wh + default_bbox_xy
        pred_wh = P.Exp()(pred_loc[..., 2:] * self.prior_scaling_wh) * default_bbox_wh

        pred_xy_0 = pred_xy - pred_wh / 2.0
        pred_xy_1 = pred_xy + pred_wh / 2.0
        pred_xy = P.Concat(-1)((pred_xy_0, pred_xy_1))
        pred_xy = P.Maximum()(pred_xy, 0)
        pred_xy = P.Minimum()(pred_xy, 1)
        return pred_xy, pred_label


class ConvBNReLU(nn.Cell):
    """
    Convolution/Depthwise fused with Batchnorm and ReLU block definition.

    Args:
        in_planes (int): Input channel.
        out_planes (int): Output channel.
        kernel_size (int): Input kernel size.
        stride (int): Stride size for the first convolutional layer. Default: 1.
        groups (int): channel group. Convolution is 1 while Depthiwse is input channel. Default: 1.
        shared_conv(Cell): Use the weight shared conv, default: None.

    Returns:
        Tensor, output tensor.

    Examples:
        >>> ConvBNReLU(16, 256, kernel_size=1, stride=1, groups=1)
    """

    def __init__(self, in_planes, out_planes, kernel_size=3, stride=1, groups=1, shared_conv=None):
        super(ConvBNReLU, self).__init__()
        padding = 0
        in_channels = in_planes
        out_channels = out_planes
        if shared_conv is None:
            if groups == 1:
                conv = nn.Conv2d(in_channels, out_channels, kernel_size, stride, pad_mode='same', padding=padding)
            else:
                out_channels = in_planes
                conv = nn.Conv2d(in_channels, out_channels, kernel_size, stride, pad_mode='same',
                                 padding=padding, group=in_channels)
            layers = [conv, _bn(out_planes), nn.ReLU6()]
        else:
            layers = [shared_conv, _bn(out_planes), nn.ReLU6()]
        self.features = nn.SequentialCell(layers)

    def construct(self, x):
        output = self.features(x)
        return output


@ClassFactory.register(ModuleType.HEAD)
class WeightSharedMultiBox(nn.Cell):
    """
    Weight shared Multi-box conv layers. Each multi-box layer contains class conf scores and localization predictions.
    All box predictors shares the same conv weight in different features.

    Args:
        config (dict): The default config of SSD.
        loc_cls_shared_addition(bool): Whether the location predictor and classifier prediction share the
                                       same addition layer.
    Returns:
        Tensor, localization predictions.
        Tensor, class conf scores.
    """

    # net, Tensor(default_boxes), config
    def __init__(self, config, loc_cls_shared_addition=False):
        super(WeightSharedMultiBox, self).__init__()

        num_classes = config.num_classes
        out_channels = config.extras_out_channels[0]
        num_default = config.num_default[0]
        num_features = len(config.feature_size)
        num_addition_layers = config.num_addition_layers
        self.loc_cls_shared_addition = loc_cls_shared_addition
        self.activation = P.Sigmoid()

        # =============================
        self.default_boxes = Tensor(default_boxes)
        self.prior_scaling_xy = config.prior_scaling[0]
        self.prior_scaling_wh = config.prior_scaling[1]
        # =============================

        if not loc_cls_shared_addition:
            loc_convs = [
                _conv2d(out_channels, out_channels, 3, 1) for x in range(num_addition_layers)
            ]
            cls_convs = [
                _conv2d(out_channels, out_channels, 3, 1) for x in range(num_addition_layers)
            ]
            addition_loc_layer_list = []
            addition_cls_layer_list = []
            for _ in range(num_features):
                addition_loc_layer = [
                    ConvBNReLU(out_channels, out_channels, 3, 1, 1, loc_convs[x]) for x in range(num_addition_layers)
                ]
                addition_cls_layer = [
                    ConvBNReLU(out_channels, out_channels, 3, 1, 1, cls_convs[x]) for x in range(num_addition_layers)
                ]
                addition_loc_layer_list.append(nn.SequentialCell(addition_loc_layer))
                addition_cls_layer_list.append(nn.SequentialCell(addition_cls_layer))
            self.addition_layer_loc = nn.CellList(addition_loc_layer_list)
            self.addition_layer_cls = nn.CellList(addition_cls_layer_list)
        else:
            convs = [
                _conv2d(out_channels, out_channels, 3, 1) for x in range(num_addition_layers)
            ]
            addition_layer_list = []
            for _ in range(num_features):
                addition_layers = [
                    ConvBNReLU(out_channels, out_channels, 3, 1, 1, convs[x]) for x in range(num_addition_layers)
                ]
                addition_layer_list.append(nn.SequentialCell(addition_layers))
            self.addition_layer = nn.SequentialCell(addition_layer_list)

        loc_layers = [_conv2d(out_channels, 4 * num_default,
                              kernel_size=3, stride=1, pad_mod='same')]

        cls_layers = [_conv2d(out_channels, num_classes * num_default,
                              kernel_size=3, stride=1, pad_mod='same')]

        self.loc_layers = nn.SequentialCell(loc_layers)
        self.cls_layers = nn.SequentialCell(cls_layers)
        self.flatten_concat = FlattenConcat(config)

        self.less = P.Less()
        self.tile = P.Tile()
        self.reduce_sum = P.ReduceSum()
        self.expand_dims = P.ExpandDims()
        self.class_loss = SigmoidFocalClassificationLoss(config.gamma, config.alpha)
        self.loc_loss = nn.SmoothL1Loss()

    def construct(self, inputs):
        """forward pass"""
        loc_outputs = ()
        cls_outputs = ()
        num_heads = len(inputs)
        for i in range(num_heads):
            if self.loc_cls_shared_addition:
                features = self.addition_layer[i](inputs[i])
                loc_outputs += (self.loc_layers(features),)
                cls_outputs += (self.cls_layers(features),)
            else:
                features = self.addition_layer_loc[i](inputs[i])
                loc_outputs += (self.loc_layers(features),)
                features = self.addition_layer_cls[i](inputs[i])
                cls_outputs += (self.cls_layers(features),)

        return self.flatten_concat(loc_outputs), self.flatten_concat(cls_outputs)

    def construct_train(self, x, *args):
        """training"""
        x = self.construct(x)

        pred_loc = x[0]
        pred_label = x[1]

        pred_loc = F.cast(pred_loc, mstype.float32)
        pred_label = F.cast(pred_label, mstype.float32)

        gt_loc = args[1]

        gt_label = args[2]
        num_matched_boxes = args[3]

        mask = F.cast(self.less(0, gt_label), mstype.float32)
        num_matched_boxes = self.reduce_sum(F.cast(num_matched_boxes, mstype.float32))
        # Localization Loss
        mask_loc = self.tile(self.expand_dims(mask, -1), (1, 1, 4))
        smooth_l1 = self.loc_loss(pred_loc, gt_loc) * mask_loc
        loss_loc = self.reduce_sum(self.reduce_sum(smooth_l1, -1), -1)

        # Classification Loss
        loss_cls = self.class_loss(pred_label, gt_label)
        loss_cls = self.reduce_sum(loss_cls, (1, 2))
        return self.reduce_sum((loss_cls + loss_loc) / num_matched_boxes)

    def construct_test(self, x):
        """For eval"""
        x = self.construct(x)

        pred_loc = x[0]
        pred_label = x[1]

        pred_label = self.activation(pred_label)
        pred_loc = F.cast(pred_loc, mstype.float32)
        pred_label = F.cast(pred_label, mstype.float32)
        x = (pred_loc, pred_label)

        pred_loc = x[0]
        pred_label = x[1]
        default_bbox_xy = self.default_boxes[..., :2]
        default_bbox_wh = self.default_boxes[..., 2:]
        pred_xy = pred_loc[..., :2] * self.prior_scaling_xy * default_bbox_wh + default_bbox_xy
        pred_wh = P.Exp()(pred_loc[..., 2:] * self.prior_scaling_wh) * default_bbox_wh

        pred_xy_0 = pred_xy - pred_wh / 2.0
        pred_xy_1 = pred_xy + pred_wh / 2.0
        pred_xy = P.Concat(-1)((pred_xy_0, pred_xy_1))
        pred_xy = P.Maximum()(pred_xy, 0)
        pred_xy = P.Minimum()(pred_xy, 1)
        return pred_xy, pred_label
