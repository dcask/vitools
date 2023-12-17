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
    msg.setWindowIcon(QIcon(constants.VI_WINDOW_ICON_PATH))
    msg.exec_()
    
def throwInfo(message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText("Done")
    msg.setInformativeText(message)
    msg.setWindowTitle("Done")
    msg.setWindowIcon(QIcon(constants.VI_WINDOW_ICON_PATH))
    msg.exec_()
    
class WorkerUser(QObject):
    finished = pyqtSignal()
    catcherror = pyqtSignal(str)

    def run(self):
        # viplatform.visiology.clearData()
        if viplatform.visiology.checkPlatform():
            viplatform.visiology.getUsers()
        if viplatform.visiology.hasError:
            self.catcherror.emit(viplatform.visiology.errorText) 
        self.finished.emit()

class WorkerToken(QObject):
    finished = pyqtSignal()
    catcherror = pyqtSignal(str)

    def run(self):
        # viplatform.visiology.clearData()
        if viplatform.visiology.checkPlatform():
            viplatform.visiology.getToken()
        if viplatform.visiology.hasError:
            self.catcherror.emit(viplatform.visiology.errorText) 
        self.finished.emit()
class WorkerLicence(QObject):
    finished = pyqtSignal()
    catcherror = pyqtSignal(str)

    def run(self):
        # viplatform.visiology.clearData()
        if viplatform.visiology.checkPlatform():
            viplatform.visiology.getLicense()
        if viplatform.visiology.hasError:
            self.catcherror.emit(viplatform.visiology.errorText) 
        self.finished.emit()

class WorkerLoki(QObject):
    finished = pyqtSignal()
    catcherror = pyqtSignal(str)

    def run(self):
        # viplatform.visiology.clearData()
        if viplatform.visiology.checkPlatform():
            viplatform.visiology.getLokiDashboardRequests()
        if viplatform.visiology.hasError:
            self.catcherror.emit(viplatform.visiology.errorText) 
        self.finished.emit()
        
class LoadingGif(QWidget): 
    
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.setFixedSize(50,50)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        geo = self.geometry()
        geo.moveCenter(parent.geometry().center())
        self.setGeometry(geo)
        
        
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
    
    # def sho(self): 
    #         self.movie.stop()
    #         self.close()