import sys

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import ReversibleWatermark
import login


class LoginCode(QMainWindow, login.Ui_MainWindow):
    def __init__(self, parent=None):
        super(LoginCode, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # 隐藏边框
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.reversibleWatermarkWindow = ReversibleWatermark.ReversibleWatermark()
        self.connector()
        self.add_shadow()

    def connector(self):
        self.pushButton_login.clicked.connect(self.checkLogin)
        self.Button_close.clicked.connect(self.onCloseButtonClicked)

    def onCloseButtonClicked(self):
        self.close()

    def checkLogin(self):
        name = self.lineEdit_name.text()
        passwd = self.lineEdit_password.text()
        if name == "admin" and passwd == "123456":
            self.reversibleWatermarkWindow.show()
            self.close()
        else:
            QMessageBox.critical(self, '警告', '登录失败！')

    def add_shadow(self):
        # 添加阴影
        self.effect_shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self.effect_shadow.setOffset(0, 0)  # 偏移
        self.effect_shadow.setBlurRadius(20)  # 阴影半径
        self.effect_shadow.setColor(QColor(114, 114, 114))  # 阴影颜色
        self.login.setGraphicsEffect(self.effect_shadow)  # 将设置套用到widget窗口中

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
    main = LoginCode()
    # 创建窗口
    main.show()
    # 进入程序的主循环，并通过exit函数，确保主循环安全结束
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
