# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 20:43:24 2023

@author: dcask
"""
import sys
import constants
import viplatform
import viutils
from loginwindow import ViLogin
from tabpanel import ViTabPanel
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QSize, QTimer, QThread
from PyQt5.QtWidgets import QVBoxLayout, QWidget

# ------- Main Window Class
class MainWindow(QMainWindow):
    
    def __init__(self):
        super(MainWindow,self).__init__()
        
        self.centralwidget=QWidget(self)
        self.setMinimumSize(QSize(constants.VI_WINDOW_WIDTH, constants.VI_WINDOW_HEIGHT))    
        self.setWindowTitle(constants.VI_WINDOW_NAME)
        self.setWindowIcon(QtGui.QIcon(constants.VI_WINDOW_ICON_PATH))
        self.viTabPanel=ViTabPanel(self.centralwidget)
        self.centralLayout= QVBoxLayout(self.centralwidget)
        self.centralLayout.addWidget(self.viTabPanel)
        self.setCentralWidget(self.centralwidget)
    #-------------------- press login ------------------
    def login(self):
        loginDlg = ViLogin(self)

        if not loginDlg.exec(): 
            self.close()
        else:
            if viplatform.init(loginDlg.username, loginDlg.password, loginDlg.baseURL):
                loginDlg.saveURL()
                viplatform.visiology.windowCentralWidget=self.centralwidget
                self.clickRefresh()
                self.refreshToken()
            else:
                viutils.throwError(viplatform.visiology.errorText)
                QTimer.singleShot(10, self.login)
    def clickRefresh(self):
        self.loader= viutils.LoadingGif(self.centralwidget)
        self.thread = QThread()
        self.workerTokenA = viutils.WorkerToken()
        self.workerUser = viutils.WorkerUser()
        self.workerLicence = viutils.WorkerLicence()
        self.workerLoki = viutils.WorkerLoki()
        self.workerTokenA.moveToThread(self.thread)
        self.workerUser.moveToThread(self.thread)
        self.workerLicence.moveToThread(self.thread)
        self.workerLoki.moveToThread(self.thread)
        
        self.thread.started.connect(self.workerTokenA.run)
        self.thread.started.connect(self.workerUser.run)
        self.thread.started.connect(self.workerLicence.run)
        self.thread.started.connect(self.workerLoki.run)
        
        self.workerTokenA.finished.connect(self.thread.quit)
        self.workerTokenA.finished.connect(self.workerTokenA.deleteLater)
        self.workerTokenA.catcherror.connect(viutils.throwError)
        
        self.workerUser.finished.connect(self.thread.quit)
        self.workerUser.finished.connect(self.workerUser.deleteLater)
        self.workerUser.catcherror.connect(viutils.throwError)
        
        self.workerLicence.finished.connect(self.thread.quit)
        self.workerLicence.finished.connect(self.workerLicence.deleteLater)
        self.workerLicence.catcherror.connect(viutils.throwError)
        
        self.workerLoki.finished.connect(self.thread.quit)
        self.workerLoki.finished.connect(self.workerLoki.deleteLater)
        self.workerLoki.catcherror.connect(viutils.throwError)
        
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        
        self.thread.finished.connect(
            lambda: self.viTabPanel.init()
        )
        self.thread.finished.connect(
            lambda: self.loader.stopAnimation()
        )
        
    def refreshToken(self):
        self.threadToken = QThread()
        self.workerToken = viutils.WorkerToken()
        
        self.workerToken.moveToThread(self.threadToken)
        
        self.threadToken.started.connect(self.workerToken.run)
        
        self.workerToken.finished.connect(self.threadToken.quit)
        self.workerToken.finished.connect(self.workerToken.deleteLater)
        self.workerToken.catcherror.connect(viutils.throwError)
              
        self.threadToken.finished.connect(self.threadToken.deleteLater)
        self.threadToken.start()
        QTimer.singleShot(60*1000*58, self.refreshToken)
        self.threadToken.finished.connect(
            lambda: self.viTabPanel.tab1.refreshView()
        )
    def closeEvent(self, event):
        self.viTabPanel.close()
        event.accept()
    def show(self):
        QMainWindow.show(self)
        QTimer.singleShot(0, self.login)
#------- main routine ---------------------------------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
     
    sys.exit( app.exec_() )