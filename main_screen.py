# 모듈 ======================================================================================
import os
import sys
import numpy as np
import cv2 as cv
import time
import threading

from PyQt5.QtCore import QSize,Qt,QThread,QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
import piexif

from multiprocessing import Process
from threading import Thread
# ===========================================================================================

mainScreen = uic.loadUiType("MainScreen.ui")[0]

'''동영상 재생 스레드'''
class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QThread,np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        

    def run(self):
        cap = cv.VideoCapture(self.fname) # 파일에서 영상을 불러와 캡쳐
        FPS = cap.get(cv.CAP_PROP_FPS) # 초당 프레임 수
        # 영상 재생
        # _run_flag에 따라 재생/멈춤 결정
        while True:
            if self._run_flag: # 재생
                ret, cv_img = cap.read()
                if ret: # 동영상 모두 재생 전
                    self.change_pixmap_signal.emit(self,cv_img) # (스레드 본인,이미지)
                    # 동영상 속도 조절 (정확하지는 않지만 가장 일반적임)
                    time.sleep(1/FPS)
                else: # 동영상 모두 재생 시 종료
                    break
            else: # 멈춤
                time.sleep(0.5)
        # capture 종료
        cap.release()

    # 재생 버튼 클릭 메소드
    def play(self):
        self._run_flag = True
       
    # 멈춤 버튼 클릭 메소드
    def pause(self):
        self._run_flag = False


    def stop(self):
        # run flag를 False로 하고 스레드 종료를 기다림
        self._run_flag = False
        self.wait()

    def setFilename(self,fname):
        # 파일명 설정
        self.fname = fname



'''사용자 설정 스크린'''
class OptionScreen(QDialog):
    def __init__(self):
        super(OptionScreen,self).__init__()
        self.ui = uic.loadUi('OptionScreen.ui',self)

        # self.setupUi(self)

'''메인 스크린'''
class MainScreen(QMainWindow, mainScreen):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        # camSelcCombobox에 아이템 추가
        self.setup_camSelcCombobox(self.camSelcCombobox)
        # modeSelcCombobox에 아이템 추가
        self.setup_modeSelcCombobox(self.modeSelcCombobox)

        '''버튼에 기능을 연결하는 코드'''
        # 재생/멈춤 버튼
        self.playerBtn.clicked.connect(self.playerBtnClicked)
        # 사운드 버튼
        self.soundBtn.clicked.connect(self.soundBtnClicked)
        # 설정 버튼
        self.optionBtn.clicked.connect(self.optionBtnClicked)

        '''스레드 관련 코드'''
        # 캠 스레드 4개 생성
        self.cam = [0,0,0,0]
        for i in range(4):
            self.cam[i] = VideoThread()

        self.frame = {self.cam[0]:self.camView1,
                    self.cam[1]:self.camView2,
                    self.cam[2]:self.camView3,
                    self.cam[3]:self.camView4}

        # 캠 스레드에서 출력될 비디오 설정
        self.setVideo2Thread()
        # 캠 스레드 시작 (캠 출력 시작)
        self.startThread()
        # 비디오 출력 화면 크기(모든 화면의 크기가 동일하다고 가정)
        self.display_width = 426
        self.display_height = 240

    '''콤보박스 셋업'''
    def setup_camSelcCombobox(self,combobox):
        combobox.addItem("Main")
        combobox.addItem("Camera 1")
        combobox.addItem("Camera 2")
        combobox.addItem("Camera 3")
        combobox.addItem("Camera 4")

    def setup_modeSelcCombobox(self,combobox):
        combobox.addItem("day mode")
        combobox.addItem("night mode")
        combobox.addItem("auto mode")

    '''버튼 클릭 메서드'''
    def playerBtnClicked(self):
        # TODO: 재생 버튼 클릭 시의 동작
        raise Exception.implementationError
    def soundBtnClicked(self):
        # TODO: 사운드 버튼 클릭 시의 동작
        raise Exception.implementationError
    def optionBtnClicked(self) :
        self.optionScreen = OptionScreen()
        self.optionScreen.exec_()

    '''스레드 관련 메서드'''


    # 각 캠 스레드에서 출력될 비디오 할당
    def setVideo2Thread(self):
        self.cam[0].setFilename("sample_video/lol03_40ms_wind.mp4")
        self.cam[1].setFilename("sample_video/lol04_60ms_wind.mp4")
        self.cam[2].setFilename("sample_video/lol05_80ms_wind.mp4")
        self.cam[3].setFilename("sample_video/Sample MP4 Video File for Testing.mp4")

    def startThread(self):
        for i in range(4):
            self.cam[i].change_pixmap_signal.connect(self.update_image)
            self.cam[i].start()

    @pyqtSlot(QThread,np.ndarray)
    def update_image(self,thread,cv_img):
        # 이미지 뷰어를 새로운 이미지로 업데이트
        qt_img = self.convert_cv_qt(cv_img)
        self.frame[thread].setPixmap(qt_img)
        # frame.setPixmap(qt_img)
        # self.camView1.setPixmap(qt_img)
        # self.camView2.setPixmap(qt_img)
        # self.camView3.setPixmap(qt_img)
        # self.camView4.setPixmap(qt_img)

    def convert_cv_qt(self,cv_img):
        # opencv 이미지에서 QPixmap 이미지로 변환
        gray_image = cv.cvtColor(cv_img,cv.COLOR_BGR2GRAY)
        # print(rgb_image.shape)
        # 높이, 너비 값 가져오기
        h,w = gray_image.shape
        #bytes_per_line = ch*w
        # opencv 이미지를 QImage로 변환
        convert_to_Qt_format = QImage(gray_image,w,h,QImage.Format_Grayscale8)
        # 동영상 스케일 조정
        p = convert_to_Qt_format.scaled(self.display_width,self.display_height,Qt.KeepAspectRatio)

        return QPixmap.fromImage(p)

    def closeEvent(self,event):
        for i in range(4):
            self.cam[i].terminate()

        event.accept()





if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = MainScreen()
    myWindow.show()
    app.exec_()