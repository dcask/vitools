# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 15:31:52 2024

@author: dcask
"""

import constants
import viplatform
from viutils import WorkerRestartServer, LoadingGif, throwError
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget,  QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QPushButton
from PyQt5.QtWidgets import QLineEdit, QFrame, QScrollArea, QSpacerItem, QDialog, QDialogButtonBox
from PyQt5.QtCore import Qt, QSize, QThread


#------------------------------------------------------------------------------
class ScrollMessageBox(QDialog):
    def __init__(self, l):
        super().__init__()
        self.setWindowTitle("LOG")
        self.centralwidgetLayout = QVBoxLayout(self)
        self.groupWidget = QWidget(self)
        self.groupLayout = QGridLayout(self.groupWidget)
    
        QBtn = QDialogButtonBox.Close
    
        self.buttonBox = QDialogButtonBox(QBtn)
    
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidget = QWidget()

        self.scrollAreaWidgetLayout = QVBoxLayout(self.scrollAreaWidget)
        self.scrollAreaWidgetLayout.addItem(QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        self.scrollArea.setWidget(self.scrollAreaWidget)
        self.groupLayout.addWidget(self.scrollArea)
        
        # lay = QVBoxLayout(self)
        for item in l:
            lay=QLabel(item, self)
            count = self.scrollAreaWidgetLayout.count() - 1
            self.scrollAreaWidgetLayout.insertWidget(count, lay)
        # self.layout().addWidget(scroll, 0, 0, 1, self.layout().columnCount())
        # self.setStyleSheet("QScrollArea{min-width:300 px; min-height: 400px}")
    
    	
    	# message = QLabel("Something happened, is that OK?")
    	# self.layout.addWidget(message)
    	# self.layout.addWidget(self.buttonBox)
        self.centralwidgetLayout.addWidget(self.groupWidget)
      
#------------------------------------------------------------------------------
class ViShellTab(QWidget):
    def __init__(self, parent): 
        super(QWidget, self).__init__(parent) 
        self.centralwidgetLayout = QVBoxLayout(self)
        self.services=[]
        
        self.groupWidget = QWidget(self)
        self.groupLayout = QGridLayout(self.groupWidget)
        
        # self.messageLabel = QLabel()
        # self.messageLabel.setText(constants.VI_SHELL_MESSAGE_LABEL)
        
        # self.message = QLineEdit()
        # self.sendButton = QPushButton(constants.VI_SHELL_SEND_BUTTON_LABEL, self)
        # self.sendButton.setStyleSheet('QPushButton {background-color: #dd556d}')
        # self.sendButton.clicked.connect(self.clickSendMessage)
        
        self.refreshButton = QPushButton(constants.VI_SHELL_REFRESH_BUTTON_LABEL, self)
        self.refreshButton.setStyleSheet('QPushButton {background-color: #dd556d}')
        self.refreshButton.clicked.connect(self.init)
        
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidget = QWidget()

        self.scrollAreaWidgetLayout = QVBoxLayout(self.scrollAreaWidget)
        self.scrollAreaWidgetLayout.addItem(QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        self.scrollArea.setWidget(self.scrollAreaWidget)
        
        # self.groupLayout.addWidget(self.messageLabel, 0, 0, 1, 1, Qt.AlignRight)
        # self.groupLayout.addWidget(self.message, 0, 1, 1, 1)
        self.groupLayout.addWidget(self.refreshButton, 0, 0, 1, 1)
        self.groupLayout.addWidget(self.scrollArea, 1, 0, 2, 1)
        
        self.centralwidgetLayout.addWidget(self.groupWidget)
        
        # self.linkButton = QPushButton(constants.VI_ACCESS_BUTTON_LABEL, self)
        # self.linkButton.setStyleSheet('QPushButton {background-color: #3e1391;color:white;}')
        # self.linkButton.clicked.connect(self.clickLinkMethod)

        # self.linkButton.setEnabled(False)
        # self.groupLayout.addWidget(self.linkButton, 5, 1, 1, 1)
#------------------------------------------------------------------------------        
    # def clickSendMessage(self):  
    #     viplatform.visiology.sendAdminMessage(self.message.text())
#------------------------------------------------------------------------------        
    def clickRestart(self):  
        sender = self.sender()

        self.loader= LoadingGif(self)
        self.thread = QThread()
        self.worker = WorkerRestartServer(sender.property('service'))
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.catcherror.connect(throwError)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        self.thread.finished.connect(
            lambda: self.loader.stopAnimation()
        )
        self.thread.finished.connect(
            lambda: self.init()
        )
        
        # viplatform.visiology.restartService(sender.property('service'))
        # throwInfo(sender.property('service'))
#------------------------------------------------------------------------------        
    def clickLog(self):  
        sender = self.sender()
        value = viplatform.visiology.getServiceLog(sender.property('service'))
        # result = ScrollMessageBox(', '.join(value['details']), None)
        result = ScrollMessageBox(value['details'])
        result.resize(500, 500)
        result.exec_()
        # throwInfo(', '.join(value['details']))
#------------------------------------------------------------------------------        
    def init(self):
        for i in self.services: i.deleteLater()
        self.services=[]
        while self.scrollAreaWidgetLayout.count():
            child = self.scrollAreaWidgetLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        viplatform.visiology.getServices()
        services= sorted(viplatform.visiology.services, key=lambda d: d['name']) 
        print('f')
        for service in services:
            restart_button=QPushButton('Restart', self)
            restart_button.setProperty('service', service['name'])
            restart_button.setStyleSheet('QPushButton {background-color: #f5b25c}')
            restart_button.clicked.connect(self.clickRestart)
            
            log_button=QPushButton('Log', self)
            log_button.setProperty('service', service['name'])
            log_button.setStyleSheet('QPushButton {background-color: #76b6f9}')
            log_button.clicked.connect(self.clickLog)
            
            count = self.scrollAreaWidgetLayout.count() - 1
            
            buttonGroup = QWidget()
            buttonGroupLayout =QHBoxLayout(buttonGroup)
            serviceLabel = QLabel()
            serviceLabel.setText(service['name'].replace('visiology2_','').upper())
            replicaLabel = QLabel()
            replicaLabel.setText(service['replicas'])
            if service['replicas'][0:1]=='0':
                replicaLabel.setStyleSheet('color: red')
            buttonGroupLayout.addWidget(serviceLabel)
            buttonGroupLayout.addWidget(replicaLabel)
            buttonGroupLayout.addWidget(restart_button)
            buttonGroupLayout.addWidget(log_button)
            line= QFrame(self)
            line.setFrameShape(QFrame.HLine)
            self.scrollAreaWidgetLayout.insertWidget(count, buttonGroup)
            self.scrollAreaWidgetLayout.insertWidget(count, line)
            
            self.services.append(buttonGroup)
            
