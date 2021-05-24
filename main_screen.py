import os
import sys
import numpy as np
import cv2 as cv
import time
import threading

from PyQt5.QtCore import QSize,Qt,QThread,QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.uic import loadUi
from PyQt5.QtGui import *
import piexif

from multiprocessing import Process
from threading import Thread
import threader



form_class = uic.loadUiType("main.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        #버튼에 기능을 연결하는 코드
        self.MotionVectorButton.clicked.connect(self.button1Function)
        self.SoundFeatureButton.clicked.connect(self.button2Function)

    #btn_1이 눌리면 작동할 함수
    # 움직임 벡터 추출기 팝업 버튼
    def button1Function(self) :
        motion_click = MotionClick()
        motion_click.exec_()


    #btn_2가 눌리면 작동할 함수
    #소리 특징점 추출기 팝업 버튼
    def button2Function(self) :
        sound_click = SoundClick()
        sound_click.exec_()






if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()