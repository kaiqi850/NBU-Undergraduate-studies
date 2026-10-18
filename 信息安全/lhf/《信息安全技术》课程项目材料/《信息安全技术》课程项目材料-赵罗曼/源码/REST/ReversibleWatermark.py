import sys

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import webbrowser

import rest
import Model1
import Model2
import cv2 as cv2
import csv
import time

class HoverHighlightDelegate(QStyledItemDelegate):
    def __init__(self, tableWidget, parent=None):
        super(HoverHighlightDelegate, self).__init__(parent)
        self.tableWidget = tableWidget

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
        if option.state and QStyle.State_MouseOver:
            hoverItem = self.tableWidget.item(index.row(), index.column())
            if hoverItem is not None:
                row = hoverItem.row()
                columnCount = self.tableWidget.columnCount()
                for i in range(columnCount):
                    item = self.tableWidget.item(row, i)
                    if item is not None:
                        modelIndex = self.tableWidget.model().index(row, i)
                        op = option
                        op.index = modelIndex
                        op.rect = self.tableWidget.visualItemRect(item)
                        super().paint(painter, op, modelIndex)
            return
        return super().paint(painter, option, index)


class IconDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(IconDelegate, self).initStyleOption(option, index)
        if option.features & QtWidgets.QStyleOptionViewItem.HasDecoration:
            s = option.decorationSize
            s.setWidth(option.rect.width())
            option.decorationSize = s


class ReversibleWatermark(QMainWindow, rest.Ui_MainWindow):
    def __init__(self, parent=None):
        super(ReversibleWatermark, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # 隐藏边框
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.tableWidget.setItemDelegate(HoverHighlightDelegate(self.tableWidget))
        delegate = IconDelegate(self.tableWidget)
        self.tableWidget.setItemDelegate(delegate)
        self.init()
        self.timerInit()
        self.connector()
        self.add_shadow()
        self.intithome()

    def intithome(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/leftside/pictures/主页首页2.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.Button_home.setIcon(icon)
        self.Button_home.setStyleSheet("color:rgb(14, 119, 249);background-color:rgb(215, 231, 246);")
        ##########修改头像#############
        self.Avatar.setStyleSheet("QFrame#Avatar{\n"
                                  "    border-image: url(./touxiang/1.jpg);\n"
                                  "    border-radius:12px;\n"
                                  "    background-color: rgb(255, 255, 255);\n"
                                  "}")

    def init(self):
        self.stackedWidget.setCurrentIndex(2)
        self.__filePath = []
        self.__imageComplete = []
        self.__dealType = 0  # 0加密/1认证/2修复
        self.__framesLoad = [self.Frame_load1, self.Frame_load2, self.Frame_load3, self.Frame_load4, self.Frame_load5]
        self.__labelPic = [self.Lable_pic1, self.Lable_pic2, self.Lable_pic3, self.Lable_pic4, self.Lable_pic5]
        self.__labelComplete = [self.Lable_pic1_2, self.Lable_pic2_2, self.Lable_pic3_2, self.Lable_pic4_2,
                                self.Lable_pic5_2]
        self.__TextPic = [self.Text_Picname1, self.Text_Picname2, self.Text_Picname3, self.Text_Picname4,
                          self.Text_Picname5]
        self.__TextPicComplete = [self.Text_Picname1_2, self.Text_Picname2_2, self.Text_Picname3_2,
                                  self.Text_Picname4_2, self.Text_Picname5_2]
        self.__TextLoad = [self.Text_loadstatus1, self.Text_loadstatus2, self.Text_loadstatus3, self.Text_loadstatus4,
                           self.Text_loadstatus5]
        self.__proBar = [self.progressBar1, self.progressBar1_2, self.progressBar1_3, self.progressBar1_4,
                         self.progressBar1_5]
        self.__framesComplete = [self.Frame_complete1, self.Frame_complete2, self.Frame_complete3, self.Frame_complete4,
                                 self.Frame_complete5]
        self.__textLoadShow = ['待加密', '待认证', '待修复', '正在加密中...', '正在认证中...', '正在修复中...',
                               '已加密', '已认证', '已修复']

    def timerInit(self):
        self.__timer = QTimer()
        self.__timer.timeout.connect(self.updateProgressBar)

    def connector(self):
        self.Button_min.clicked.connect(self.onSmallButtonClicked)
        self.Button_close.clicked.connect(self.onCloseButtonClicked)
        self.vipButton.clicked.connect(self.onvipButtonClicked)
        self.Button_encrypt.mousePressEvent = lambda event: self.turnToAddPicturePage(0)
        self.Button_tamper.mousePressEvent = lambda event: self.turnToAddPicturePage(1)
        self.Button_repair.mousePressEvent = lambda event: self.turnToAddPicturePage(2)
        self.Button_home.mousePressEvent = lambda event: self.turnToAddPicturePage(3)
        self.Button_log.mousePressEvent = lambda event: self.turnToAddPicturePage(4)
        self.Button_home1.mousePressEvent = lambda event: self.turnToAddPicturePage(0)
        self.Button_home2.mousePressEvent = lambda event: self.turnToAddPicturePage(1)
        self.Button_home3.mousePressEvent = lambda event: self.turnToAddPicturePage(2)
        self.Button_addpic.clicked.connect(self.addPictureAndDeal)
        self.Button_Download1.mousePressEvent = lambda event: self.downloadDealPic(0)
        self.Button_Download2.mousePressEvent = lambda event: self.downloadDealPic(1)
        self.Button_Download3.mousePressEvent = lambda event: self.downloadDealPic(2)
        self.Button_Download4.mousePressEvent = lambda event: self.downloadDealPic(3)
        self.Button_Download5.mousePressEvent = lambda event: self.downloadDealPic(4)

    def onSmallButtonClicked(self):
        self.showMinimized()

    def onCloseButtonClicked(self):
        self.close()

    #跳转到网页
    def onvipButtonClicked(self):
        webbrowser.open('https://lhfgghc.github.io/en/blog/labrecordsegmentation/')


    def turnToAddPicturePage(self, dealType):
        self.__imageComplete = []
        self.__dealType = dealType
        if dealType == 3:
            self.stackedWidget.setCurrentIndex(2)
        elif dealType == 4:
            self.stackedWidget.setCurrentIndex(3)
            self.showLog()
        else:
            self.stackedWidget.setCurrentIndex(0)

        # ---------设置按钮变色---------#
        if dealType == 0:
            # 恢复
            self.reco2()
            self.reco3()
            self.recohome()
            self.recolog()

            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/leftside/pictures/图像加密 2.png"), QtGui.QIcon.Normal,
                           QtGui.QIcon.Off)
            self.Button_encrypt.setIcon(icon)
            self.Button_encrypt.setStyleSheet("color:rgb(14, 119, 249);background-color:rgb(215, 231, 246);")
        elif dealType == 1:
            # 恢复
            self.reco1()
            self.reco3()
            self.recohome()
            self.recolog()

            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/leftside/pictures/其他信息篡改 2.png"), QtGui.QIcon.Normal,
                           QtGui.QIcon.Off)
            self.Button_tamper.setIcon(icon)
            self.Button_tamper.setStyleSheet("color:rgb(14, 119, 249);background-color:rgb(215, 231, 246);")
        elif dealType == 2:
            self.reco1()
            self.reco2()
            self.recohome()
            self.recolog()

            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/leftside/pictures/repair-station 2.png"), QtGui.QIcon.Normal,
                           QtGui.QIcon.Off)
            self.Button_repair.setIcon(icon)
            self.Button_repair.setStyleSheet("color:rgb(14, 119, 249);background-color:rgb(215, 231, 246);")
        elif dealType == 3:
            self.reco1()
            self.reco2()
            self.reco3()
            self.recolog()

            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/leftside/pictures/主页首页2.png"), QtGui.QIcon.Normal,
                           QtGui.QIcon.Off)
            self.Button_home.setIcon(icon)
            self.Button_home.setStyleSheet("color:rgb(14, 119, 249);background-color:rgb(215, 231, 246);")
        elif dealType == 4:
            self.reco1()
            self.reco2()
            self.reco3()
            self.recohome()

            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/leftside/pictures/记录2.png"), QtGui.QIcon.Normal,
                           QtGui.QIcon.Off)
            self.Button_log.setIcon(icon)
            self.Button_log.setStyleSheet("color:rgb(14, 119, 249);background-color:rgb(215, 231, 246);")

    # 恢复
    def recohome(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/leftside/pictures/主页首页1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Button_home.setIcon(icon)
        self.Button_home.setStyleSheet("")
    def reco1(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/leftside/pictures/图像加密1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Button_encrypt.setIcon(icon)
        self.Button_encrypt.setStyleSheet("")

    def reco2(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/leftside/pictures/其他信息篡改 1.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.Button_tamper.setIcon(icon)
        self.Button_tamper.setStyleSheet("")

    def reco3(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/leftside/pictures/repair-station 1.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.Button_repair.setIcon(icon)
        self.Button_repair.setStyleSheet("")

    def recolog(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/leftside/pictures/记录 1.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.Button_log.setIcon(icon)
        self.Button_log.setStyleSheet("")

    def addPictureAndDeal(self):
        filePath = QFileDialog.getOpenFileNames(self.centralwidget, '打开文件', '.', '*.bmp;;*.jpg;;*.png')
        if len(filePath[0]) == 0:
            return
        self.stackedWidget.setCurrentIndex(1)
        self.__filePath = filePath[0]

        dealContent = ["图像加密", "篡改认证", "自修复"]
        fileNameList = [self.__filePath[i].split("/")[-1] for i in range(len(self.__filePath))]
        timeInput = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        with open("./resources/log.csv", "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            for index in range(len(self.__filePath)):
                inputRow = [timeInput, self.__filePath[index], fileNameList[index], dealContent[self.__dealType]]
                writer.writerow(inputRow)

        for leftIndex in range(len(self.__filePath), 5):
            opLoad = QtWidgets.QGraphicsOpacityEffect()
            opLoad.setOpacity(0)
            self.__framesLoad[leftIndex].setGraphicsEffect(opLoad)
        for completeIndex in range(5):
            opComplete = QtWidgets.QGraphicsOpacityEffect()
            opComplete.setOpacity(0)
            self.__framesComplete[completeIndex].setGraphicsEffect(opComplete)
        self.__progressBarIndex = 0
        self.__progressBarStep = [0 for _ in range(5)]
        for showIndex in range(0, len(self.__filePath)):
            image = QPixmap(self.__filePath[showIndex]).scaled(self.__labelPic[showIndex].size(), Qt.KeepAspectRatio)
            self.__labelPic[showIndex].setPixmap(image)
            self.__labelPic[showIndex].setFixedSize(image.width(), image.height())
            fileName = self.__filePath[showIndex].split("/")[-1]
            self.__TextPic[showIndex].setText(fileName)
            self.__TextLoad[showIndex].setText(self.__textLoadShow[self.__dealType])
            self.__proBar[showIndex].setValue(self.__progressBarStep[0])
        self.__timer.start(20)
        for showIndex in range(0, len(self.__filePath)):
            sourceNumpy = cv2.imread(self.__filePath[showIndex])
            if self.__dealType == 0:
                dealNumpy = Model1.Embedded_watermark(sourceNumpy)
            elif self.__dealType == 1:
                dealNumpy, _ = Model2.Fix_Picture(sourceNumpy)
            else:
                _, dealNumpy = Model2.Fix_Picture(sourceNumpy)
            dealNumpy = dealNumpy.astype("uint8")
            dealNumpy = cv2.cvtColor(dealNumpy, cv2.COLOR_BGR2RGB)
            image = QtGui.QImage(dealNumpy[:], dealNumpy.shape[1], dealNumpy.shape[0], dealNumpy.shape[1] * 3,
                                 QtGui.QImage.Format_RGB888)
            self.__imageComplete.append(QPixmap(image))
            self.__TextPicComplete[showIndex].setText(self.__filePath[showIndex].split("/")[-1])
            pixmap = QPixmap(image).scaled(self.__labelComplete[showIndex].size(), Qt.KeepAspectRatio)
            self.__labelComplete[showIndex].setPixmap(QtGui.QPixmap(pixmap))
            self.__labelComplete[showIndex].setFixedSize(pixmap.width(), pixmap.height())

    def updateProgressBar(self):
        if self.__progressBarIndex < len(self.__filePath):
            if self.__progressBarStep[self.__progressBarIndex] == 0:
                self.__TextLoad[self.__progressBarIndex].setText(self.__textLoadShow[3 + self.__dealType])
                self.__TextLoad[self.__progressBarIndex].repaint()
            self.__progressBarStep[self.__progressBarIndex] += 1
            self.__proBar[self.__progressBarIndex].setValue(self.__progressBarStep[self.__progressBarIndex])
            if self.__progressBarStep[self.__progressBarIndex] >= 100:
                opComplete = QtWidgets.QGraphicsOpacityEffect()
                opComplete.setOpacity(100)
                self.__framesComplete[self.__progressBarIndex].setGraphicsEffect(opComplete)
                self.__TextLoad[self.__progressBarIndex].setText(self.__textLoadShow[6 + self.__dealType])
                self.__TextLoad[self.__progressBarIndex].repaint()
                self.__progressBarIndex += 1
        else:
            # showInfo = ['加密', '认证', '修复']
            # QMessageBox.about(self, "提示", showInfo[self.__dealType] + '完成！')
            self.__timer.stop()

    def showLog(self):
        logList = [[], [], [], []]
        with open("./resources/log.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                for index in range(4):
                    logList[index].insert(0, line[index])
        self.tableWidget.setRowCount(len(logList[0]))
        for index in range(len(logList[0])):
            self.tableWidget.setItem(index, 0, QTableWidgetItem(logList[0][index]))
            item = QTableWidgetItem()
            icon = QIcon(logList[1][index])
            item.setIcon(QIcon(icon))
            self.tableWidget.setItem(index, 1, item)
            self.tableWidget.setItem(index, 2, QTableWidgetItem(logList[2][index]))
            self.tableWidget.setItem(index, 3, QTableWidgetItem(logList[3][index]))
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        # self.tableWidget.resizeColumnsToContents()  # 随内容变单元格大小
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 设置字体加粗
        font = self.tableWidget.horizontalHeader().font()
        font.setBold(True)
        self.tableWidget.horizontalHeader().setFont(font)
        # 设置单元格宽度
        self.tableWidget.horizontalHeader().resizeSection(0, 150)
        self.tableWidget.horizontalHeader().resizeSection(1, 50)
        self.tableWidget.horizontalHeader().resizeSection(2, 110)
        self.tableWidget.horizontalHeader().resizeSection(3, 100)
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.setShowGrid(False)

    def downloadDealPic(self, n):
        fd, type = QFileDialog.getSaveFileName(self.centralwidget, "保存图片", "", "*.bmp")
        self.__imageComplete[n].save(fd)

    # --------界面------------#
    def add_shadow(self):
        # 添加阴影
        self.effect_shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self.effect_shadow.setOffset(0, 0)  # 偏移
        self.effect_shadow.setBlurRadius(20)  # 阴影半径
        self.effect_shadow.setColor(QColor(64, 64, 64))  # 阴影颜色
        self.shadow.setGraphicsEffect(self.effect_shadow)  # 将设置套用到widget窗口中

    def mousePressEvent(self, evt):  # 实现自由拖动界面功能
        if evt.button() == Qt.LeftButton:
            self.switch = True
        else:
            self.switch = False

        self.mouse_x = evt.globalX()
        self.mouse_y = evt.globalY()
        self.window_x = self.x()
        self.window_y = self.y()

    def mouseMoveEvent(self, evt):
        if self.switch:
            move_x = evt.globalX() - self.mouse_x
            move_y = evt.globalY() - self.mouse_y

            vector_x = self.window_x + move_x
            vector_y = self.window_y + move_y
            self.move(vector_x, vector_y)


def main():
    # 界面显示完全
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    # 创建app实例，并传入参数
    app = QApplication(sys.argv)
    # 创建对象
    main = ReversibleWatermark()
    # 创建窗口
    main.show()
    # 进入程序的主循环，并通过exit函数，确保主循环安全结束
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
