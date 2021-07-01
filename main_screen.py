# 모듈 ======================================================================================
import os
import sys
import numpy as np
import cv2 as cv
import time
# import threading

from PyQt5.QtCore import QSize,Qt,QThread,QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
# import piexif

# from threading import Thread
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

        '''콤보박스에 함수를 연결하는 코드'''
        self.camSelcCombobox.currentIndexChanged.connect(self.camSelcComboboxChanged)
        self.modeSelcCombobox.currentIndexChanged.connect(self.modeSelcComboboxChanged)

        '''버튼에 함수를 연결하는 코드'''
        # 재생/멈춤 버튼
        self.playerBtn.clicked.connect(self.playerBtnClicked)
        # 사운드 버튼
        self.soundBtn.clicked.connect(self.soundBtnClicked)
        # 설정 버튼
        self.optionBtn.clicked.connect(self.optionBtnClicked)

        self.cam1Btn.clicked.connect(self.cam1BtnClicked)
        self.cam2Btn.clicked.connect(self.cam2BtnClicked)
        self.cam3Btn.clicked.connect(self.cam3BtnClicked)
        self.cam4Btn.clicked.connect(self.cam4BtnClicked)
        self.zoomBtn.clicked.connect(self.zoomBtnClicked)
        self.cam1Btn.setFlat(True)
        self.cam2Btn.setFlat(True)
        self.cam3Btn.setFlat(True)
        self.cam4Btn.setFlat(True)

        self.zoomFrame.hide()
        
# 170 50 901 541
        
        '''스레드 관련 코드'''
        # 캠 스레드 4개 생성
        self.cam = [0,0,0,0]
        for i in range(4):
            self.cam[i] = VideoThread()
        # 스레드에 이미지뷰 할당
        self.frame = {self.cam[0]:self.camView1,
                    self.cam[1]:self.camView2,
                    self.cam[2]:self.camView3,
                    self.cam[3]:self.camView4}

        # 캠 스레드에서 출력될 비디오 설정
        self.setVideo2Thread()
        # 캠 스레드 시작 (캠 출력 시작)
        self.startThread()
        
        # 비디오 출력 화면 크기(모든 화면의 크기가 동일하다고 가정)
        self.width1 = 900
        self.height1 = 600

        self.width2 = 426
        self.height2 = 240
        self.display_width = self.width1
        self.display_height = self.height1
        
        self.prev = self.camView1
        self.now = None
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

    '''콤보박스 선택 아이템 변경 메서드'''
    def camSelcComboboxChanged(self):
        # TODO: 카메라 선택 콤보박스 아이템 변경 시의 동작
        pass

    def modeSelcComboboxChanged(self):
        # TODO: 모드 선택 콤보박스 아이템 변경 시의 동작
        pass

    '''버튼 클릭 메서드'''
    def cam1BtnClicked(self):
        self.camView1.raise_()
        self.camView1.setGeometry(170,3,self.width1,self.height1)
        self.zoomFrame.show()
        self.zoomBtn.setFlat(True)
        self.zoomFrame.raise_()
    
    def cam2BtnClicked(self):
        self.camView2.raise_()
        self.camView2.setGeometry(170,3,self.width1,self.height1)
        self.zoomFrame.show()
        self.zoomBtn.setFlat(True)
        self.zoomFrame.raise_()
    
    def cam3BtnClicked(self):
        self.camView3.raise_()
        self.camView3.setGeometry(170,3,self.width1,self.height1)
        self.zoomFrame.show()
        self.zoomBtn.setFlat(True)
        self.zoomFrame.raise_()

    def cam4BtnClicked(self):
        self.camView4.raise_()
        self.camView4.setGeometry(170,3,self.width1,self.height1)
        self.zoomFrame.show()
        self.zoomBtn.setFlat(True)
        self.zoomFrame.raise_()
    
    def zoomBtnClicked(self):
        self.zoomFrame.hide()
        self.camView1.setGeometry(170,50,self.width2,self.height2)
        self.camView2.setGeometry(640,50,self.width2,self.height2)
        self.camView3.setGeometry(170,350,self.width2,self.height2)
        self.camView4.setGeometry(640,350,self.width2,self.height2)
        self.cam1Btn.raise_()
        self.cam2Btn.raise_()
        self.cam3Btn.raise_()
        self.cam4Btn.raise_()
        
    def playerBtnClicked(self):
        # TODO: 재생 버튼 클릭 시의 동작
        pass
    def soundBtnClicked(self):
        # TODO: 사운드 버튼 클릭 시의 동작
        pass
    def optionBtnClicked(self) :
        self.optionScreen = OptionScreen()
        self.optionScreen.exec_()

    

        
    # '''스레드 관련 메서드'''
    # 각 캠 스레드에서 출력될 비디오 할당
    def setVideo2Thread(self):
        # TODO: 캠 연결
        self.cam[0].setFilename("sample_video/1_Thunder.mp4")
        self.cam[1].setFilename("sample_video/1_Vibration.mp4")
        self.cam[2].setFilename("sample_video/2_Wind.mp4")
        self.cam[3].setFilename("sample_video/2_Vibration.mp4")

    def startThread(self):
        for i in range(4):
            self.cam[i].change_pixmap_signal.connect(self.update_image)
            self.cam[i].start()

    @pyqtSlot(QThread,np.ndarray)
    # 이미지 뷰어를 새로운 이미지로 업데이트
    def update_image(self,thread,cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.frame[thread].setPixmap(qt_img)

    # Opencv 이미지에서 QPixmap 이미지로 변환
    def convert_cv_qt(self,cvImg):
        height, width, channel = cvImg.shape
        convert_to_Qt_format = QImage(cvImg.data, width, height, QImage.Format_RGB888)
        qImg = convert_to_Qt_format.scaled(self.display_width,self.display_height,Qt.KeepAspectRatio)
        return QPixmap.fromImage(qImg)
        # gray_image = cv.cvtColor(cv_img,cv.COLOR_BGR2GRAY)
        # # print(rgb_image.shape)
        # # 높이, 너비 값 가져오기
        # h,w = gray_image.shape
        # #bytes_per_line = ch*w
        # # opencv 이미지를 QImage로 변환
        # convert_to_Qt_format = QImage(gray_image,w,h,QImage.Format_Grayscale8)
        # # 동영상 스케일 조정
        # p = convert_to_Qt_format.scaled(self.display_width,self.display_height,Qt.KeepAspectRatio)

        # return QPixmap.fromImage(p)

    def closeEvent(self,event):
        for i in range(4):
            self.cam[i].terminate()

        event.accept()





if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = MainScreen()
    myWindow.show()
    app.exec_()