# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 22:30:40 2023

@author: dcask
"""

import constants
import viplatform
from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie, QIcon
from PyQt5.QtCore import pyqtSignal, QObject


def throwError(message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("Error")
    msg.setInformativeText(message) 
    msg.setWindowTitle("Error")
    msg.setWindowIcon(QIcon(constants.img))
    msg.exec_()
    
def throwInfo(message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText("Done")
    msg.setInformativeText(message)
    msg.setWindowTitle("Done")
    msg.setWindowIcon(QIcon(constants.img))
    msg.exec_()
    
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self):
        viplatform.visiology.clearData()
        if viplatform.visiology.checkPlatform():
            viplatform.visiology.getToken()
            viplatform.visiology.getUsers()
            viplatform.visiology.getLicense()
        else:
            throwError(viplatform.visiology.errorText) 
        self.finished.emit()
  
class LoadingGif(QWidget): 
  
    def __init__(self, parent):
        super().__init__()
        self.setFixedSize(50,50)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        self.label_animation = QLabel(self)
        self.movie = QMovie(constants.VI_TABPANEL_LOADER) 
        self.label_animation.setMovie(self.movie) 
        self.startAnimation() 
        self.show()
  
    def startAnimation(self): 
        self.movie.start() 
  
    def stopAnimation(self): 
        self.movie.stop()
        self.close()