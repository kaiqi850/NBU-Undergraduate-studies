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
"""models module, import every backbone, neck, head to register classes"""
from mindvision.detection.models.backbone.darknet import CspDarkNet, DarkNet
from mindvision.detection.models.backbone.resnet import ResNet
from mindvision.detection.models.backbone.yolov5_backbone import YOLOv5Backbone
from mindvision.detection.models.backbone.mobilenet_v1 import MobileNetV1

from mindvision.detection.models.detector.faster_rcnn import FasterRCNN
from mindvision.detection.models.detector.yolo import YOLOv5, YOLOv4, YOLOv3

from mindvision.detection.models.head.roi_head import StandardRoIHead
from mindvision.detection.models.head.rpn import RPNHead
from mindvision.detection.models.head.yolo_head import YOLOv5Head, YOLOv4Head, YOLOv3Head

from mindvision.detection.models.neck.fpn import FPN
from mindvision.detection.models.neck.yolo_neck import YOLOv5Neck, YOLOv4Neck, YOLOv3Neck
from mindvision.detection.models.neck.mobilenetv1_fpn_neck import MobileNetV1FPN
from mindvision.detection.models.meta_arch.train_wrapper import TrainingWrapper, TrainingWrapperssd

from mindvision.detection.models.backbone.resnext import ResNeXt
from mindvision.detection.models.detector.mask_rcnn import MaskRCNN
from mindvision.detection.models.detector.retinanet import RetinaNet
from mindvision.detection.models.head.retina_head import RetinaHead
from mindvision.detection.models.neck.retina_fpn import RetinaFPN
from mindvision.detection.models.detection_engine.common_bbox2image import CommonDetectionEngine
from mindvision.detection.models.detection_engine.retinanet_bbox2image import RetinaDetectionEngine
from mindvision.detection.models.detection_engine.yolov5_bbbox2image import YOLOv5DetectionEngine
from mindvision.detection.models.detection_engine.ssd_bbox2image import SsdDetectionEngine

from mindvision.detection.models.detector.centerface import CenterFace
from mindvision.detection.models.backbone.mobile_v2 import MobileNetV2
from mindvision.detection.models.head.centerface_head import CenterFaceHead
from mindvision.detection.models.detection_engine.centerface_detector import CenterfaceDetectionEngine
from mindvision.detection.models.neck.centerface_neck import CenterFaceNeck
from mindvision.detection.models.head.ssd_head import WeightSharedMultiBox
from mindvision.detection.models.detector.retinaface import RetinaFace
from mindvision.detection.models.head.retinaface_head import RetinaFaceHead
from mindvision.detection.models.neck.retinaface_neck import RetinaFaceNeck
from mindvision.detection.models.detection_engine.retinaface_bbox2image import RetinafaceDetectionEngine
