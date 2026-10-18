import argparse
import platform
import shutil
import time
from numpy import random
import argparse
import os
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import ImageFont

system_font_path = "C:\\Users\\13376\\AppData\\Roaming\\Ultralytics\\Arial.ttf"
font_size = 12  # 设置字体大小
font = ImageFont.truetype(system_font_path, font_size)
from PyQt5.QtCore import *
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import *
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore, QtGui, QtWidgets
import os
import sys
from pathlib import Path

import cv2
import torch
import torch.backends.cudnn as cudnn

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = '1'
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv7 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from models.common import DetectMultiBackend
from utils.augmentations import letterbox
from utils.datasets import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from utils.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr,
                           increment_path, non_max_suppression, print_args, scale_coords, strip_optimizer, xyxy2xywh)
from utils.plots import Annotator, colors, save_one_box
from utils.torch_utils import select_device, time_sync
import numpy as np
import time

import tools.infer.utility as util
import tools.infer.predict_system as pd
import cv2


def load_model(
        weights=ROOT / 'best.pt',  # model.pt path(s)
        data=ROOT / 'data/coco128.yaml',  # dataset.yaml path
        device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        half=False,  # use FP16 half-precision inference
        dnn=False,  # use OpenCV DNN for ONNX inference

):
    # Load model
    device = select_device(device)
    model = DetectMultiBackend(weights, device=device, dnn=dnn, data=data)
    stride, names, pt, jit, onnx, engine = model.stride, model.names, model.pt, model.jit, model.onnx, model.engine

    model.to(device)

    # Half
    half &= (pt or jit or onnx or engine) and device.type != 'cpu'  # FP16 supported on limited backends with CUDA
    if pt or jit:
        model.model.half() if half else model.model.float()
    return model, stride, names, pt, jit, onnx, engine


def run(model, img, stride, pt,
        imgsz=(640, 640),  # inference size (height, width)
        conf_thres=0.8,  # confidence threshold
        iou_thres=0.15,  # NMS IOU threshold
        max_det=1000,  # maximum detections per image
        device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        classes=None,  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms=False,  # class-agnostic NMS
        augment=False,  # augmented inference
        half=False,  # use FP16 half-precision inference
        ):
    cal_detect = []

    device = select_device(device)
    names = model.module.names if hasattr(model, 'module') else model.names  # get class names

    # Set Dataloader
    im = letterbox(img, imgsz, stride, pt)[0]

    # Convert
    im = im.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
    im = np.ascontiguousarray(im)

    im = torch.from_numpy(im).to(device)
    im = im.half() if half else im.float()  # uint8 to fp16/32
    im /= 255  # 0 - 255 to 0.0 - 1.0
    if len(im.shape) == 3:
        im = im[None]  # expand for batch dim

    pred = model(im, augment=augment)

    pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
    # Process detections
    for i, det in enumerate(pred):  # detections per image
        if len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(im.shape[2:], det[:, :4], img.shape).round()

            # Write results

            for *xyxy, conf, cls in reversed(det):
                c = int(cls)  # integer class
                label = f'{names[c]}'
                lbl = names[int(cls)]
                print(lbl)
                cal_detect.append([label, xyxy])
    return cal_detect


def det_yolov7(info1):
    print(device)
    # 预加载
    args = util.parse_args(2)
    text_sys = pd.TextSystem(args)

    global model, stride, names, pt, jit, onnx, engine
    if info1[-3:] in ['jpg', 'png', 'jpeg', 'tif', 'bmp']:
        image = cv2.imread(info1)  # 读取识别对象
        w = image.shape[1]
        h = image.shape[0]
        imagecut = image[int(0.94 * h):int(h - 1), int(0.35 * w):int(0.55 * w)]

        try:
            results = run(model, image, stride, pt)  # 识别， 返回多个数组每个第一个为结果，第二个为坐标位置
            for i in results:
                box = i[1]
                p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
                color = [0, 0, 255]
                dt_boxes, rec_res = text_sys(imagecut)
                detected_cracks = []
                for rec in rec_res:
                    text, box = rec
                    if "裂缝" in text:  # 检查识别结果中是否包含“裂缝”
                        detected_cracks.append(text)

                        # 在这里你可以进一步处理文本，提取出距离信息
                        # 假设距离信息在文本中以“距离：XX米”形式出现
                        distance_info = None
                        if "距离：" in text:
                            distance_info = text.split("距离：")[1]  # 获取“距离：”后的内容

                        ui.printf(f"{text} - {box}")  # 显示识别结果

                        if distance_info:
                            ui.printf(f"Detected crack at {distance_info}")  # 显示裂缝距离信息

                if detected_cracks:
                    ui.printf(
                        str(time.strftime('%Y.%m.%d %H:%M:%S ', time.localtime(time.time()))) + '警告！检测管道裂缝')
                    cv2.rectangle(image, p1, p2, color, thickness=3, lineType=cv2.LINE_AA)


        except Exception as e:

            print(f"An error occurred: {e}")

            pass

        ui.showimg(image)
    if info1[-3:] in ['mp4', 'avi']:
        capture = cv2.VideoCapture(info1)
        stc = 0
        minutes0 = 0
        hours0 = 0
        seconds0 = 0
        while True:
            _, image = capture.read()
            if image is None:
                break

            w = image.shape[1]
            h = image.shape[0]
            imagecut = image[int(0.94 * h):int(h - 1), int(0.35 * w):int(0.55 * w)]

            stc += 1

            try:
                results = run(model, image, stride, pt)  # 识别， 返回多个数组每个第一个为结果，第二个为坐标位置

                for i in results:
                    box = i[1]
                    p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
                    color = [0, 0, 255]

                    milliseconds = capture.get(cv2.CAP_PROP_POS_MSEC)
                    seconds = milliseconds // 1000
                    milliseconds = milliseconds % 1000
                    minutes = 0
                    hours = 0
                    if seconds >= 60:
                        minutes = seconds // 60
                        seconds = seconds % 60
                    if minutes >= 60:
                        hours = minutes // 60
                        minutes = minutes % 60
                        # 处理文本信息和距离信息
                    for kk in range(len(results)):
                        txt = ''
                        deep = results[kk][0]  # 假设距离信息在第一个结果中
                        if "距离" in deep:  # 检查文本中是否包含距离信息
                            distance_info = deep.split("距离：")  # 以 "距离：" 为分隔符分割文本
                            if len(distance_info) > 1:  # 确保成功分割出距离信息
                                distance = distance_info[1]  # 提取距离信息

                        if hours != hours0 or minutes != minutes0 or seconds != seconds0:
                            hours0 = hours
                            minutes0 = minutes
                            seconds0 = seconds
                            ui.printf(str(int(hours0)) + ':' + str(int(minutes0)) + ':' + str(
                                int(seconds0)) + ' 检测管道裂缝 ' + distance)
                    # 异常处理
                    cv2.rectangle(image, p1, p2, color, thickness=3, lineType=cv2.LINE_AA)
                    if stc > 4:
                        cv2.imwrite('./images/' + str(int(hours0)) + '-' + str(int(minutes0)) + '-' + str(
                            int(seconds0)) + '-' + str(txt) + '-' + str(i[0]) + '.png', image)
            except:
                pass
            if stc > 4:
                stc = 0
            ui.showimg(image)
            QApplication.processEvents()


class Thread_1(QThread):  # 线程1
    def __init__(self, info1):
        super().__init__()
        self.info1 = info1
        # self.info1 = self.info1.to(device)
        self.run2(self.info1)

    def run2(self, info1):
        result = []
        result = det_yolov7(info1)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        MainWindow.setStyleSheet("background-image: url(\"./template/carui.png\");")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(600, 300, 721, 411))
        font = QtGui.QFont()
        font.setFamily("庞门正道标题体")
        font.setPointSize(16)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("background:rgba(0,0,0,0);")
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(80, 330, 381, 351))
        font = QtGui.QFont()
        font.setFamily("庞门正道标题体")
        font.setPointSize(14)
        self.textBrowser.setFont(font)
        self.textBrowser.setFocusPolicy(QtCore.Qt.NoFocus)
        self.textBrowser.setStyleSheet("background:rgba(0,0,0,0);")
        self.textBrowser.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.textBrowser.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.textBrowser.setObjectName("textBrowser")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(610, 870, 191, 71))
        font = QtGui.QFont()
        font.setFamily("庞门正道标题体")
        font.setPointSize(16)
        self.pushButton.setFont(font)
        self.pushButton.setStyleSheet("background:rgb(95, 210, 250);border-radius:10px;padding:2px 4px;")
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(880, 870, 191, 71))
        font = QtGui.QFont()
        font.setFamily("庞门正道标题体")
        font.setPointSize(16)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setStyleSheet("background:rgb(95, 210, 250);border-radius:10px;padding:2px 4px;")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(1140, 870, 191, 71))
        font = QtGui.QFont()
        font.setFamily("庞门正道标题体")
        font.setPointSize(16)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setStyleSheet("background:rgb(95, 210, 250);border-radius:10px;padding:2px 4px;")
        self.pushButton_3.setObjectName("pushButton_3")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        # 新增时间和日期显示的 QLabel
        self.label_datetime = QtWidgets.QLabel(self.centralwidget)
        self.label_datetime.setGeometry(QtCore.QRect(100, 40, 300, 80))  # 设置时间和日期显示 Label 的位置和大小
        font_datetime = QtGui.QFont()
        font_datetime.setFamily("庞门正道标题体")
        font_datetime.setPointSize(18)
        self.label_datetime.setFont(font_datetime)
        self.label_datetime.setStyleSheet("color: white")  # 设置时间和日期显示的字体颜色
        self.label_datetime.setObjectName("label_datetime")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # 更新时间和日期函数
        self.update_datetime()

    def update_datetime(self):
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        datetime_text = ' '.join(current_date.toString("yyyy-MM-dd")) + "\n" + ' '.join(
            ' ' + current_time.toString("hh:mm:ss"))
        self.label_datetime.setText(datetime_text)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.label_2.setText(_translate("MainWindow",
                                        "<html><head/><body><p><span style=\" font-size:18pt; font-weight:600; color:#ffffff;\">管 道 视 频 监 测</span></p></body></html>"))
        self.pushButton.setText(_translate("MainWindow", "选择站点"))
        self.pushButton_2.setText(_translate("MainWindow", "开始监控"))
        self.pushButton_3.setText(_translate("MainWindow", "停止监控"))

        # 点击文本框绑定槽事件
        self.pushButton.clicked.connect(self.openfile)
        self.pushButton_2.clicked.connect(self.click_1)
        self.pushButton_3.clicked.connect(self.handleCalc3)
        # 添加 QTimer 并启动，每秒更新一次时间和日期
        self.timer = QTimer(MainWindow)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)
        self.file_dialog = QFileDialog()

    def openfile(self):
        global sname, filepath

        self.file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        fname, _ = self.file_dialog.getOpenFileName()
        if fname == '':
            return
        filepath = os.path.normpath(fname)
        sname = filepath.split(os.sep)
        ui.printf("当前选择的站点是：%s" % filepath)

    def handleCalc3(self):
        os._exit(0)

    def printf(self, text):
        self.textBrowser.append(text)
        self.cursor = self.textBrowser.textCursor()
        self.textBrowser.moveCursor(self.cursor.End)
        QtWidgets.QApplication.processEvents()

    def showimg(self, img):
        img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img2.shape

        frame = QtGui.QImage(img2.data, w, h, ch * w, QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(frame)

        label_width = self.label_2.width()
        label_height = self.label_2.height()

        label_ratio = label_width / label_height
        video_ratio = w / h

        if label_ratio > video_ratio:
            self.label_2.setPixmap(pix.scaledToWidth(label_width))
        else:
            self.label_2.setPixmap(pix.scaledToHeight(label_height))

    def click_1(self):
        global filepath
        if filepath:  # 只有当 filepath 变量已设置时才启动线程
            try:
                self.thread_1.quit()
            except:
                pass
            self.thread_1 = Thread_1(filepath)  # 创建线程
            self.thread_1.wait()
            self.thread_1.start()  # 开始线程
        else:
            ui.printf("请先选择站点！")


if __name__ == "__main__":
    global model, stride, names, pt, jit, onnx, engine
    model, stride, names, pt, jit, onnx, engine = load_model()  # 加载模型
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
