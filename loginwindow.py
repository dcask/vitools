# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 21:57:53 2023

@author: dcask
"""


import constants

from PyQt5.QtWidgets import QComboBox, QDialog, QWidget,  QVBoxLayout, QLabel, QGridLayout, QLineEdit, QPushButton
from PyQt5 import QtGui
from PyQt5.QtCore import QSize

class ViLogin(QDialog):
    def __init__(self, parent): 
        super(QWidget, self).__init__(parent) 
        
        self.password=''
        self.username=''
        self.granted=False
        
        self.setWindowTitle(constants.VI_LOGIN_TITLE)
        self.setWindowIcon(QtGui.QIcon(constants.VI_WINDOW_ICON_PATH))
        self.setMinimumSize(QSize(constants.VI_LOGIN_WINDOW_WIDTH, constants.VI_LOGIN_WINDOW_HEIGHT))
        
        self.centralwidgetLayout = QVBoxLayout(self)
        
        self.groupWidget = QWidget(self)
        self.groupLayout = QGridLayout(self.groupWidget)
        
        #URL field
        self.urlLabel = QLabel()
        self.urlLabel.setText(constants.VI_LOGIN_URL_LABEL)

        self.urlInput = QComboBox() #QLineEdit()
        # self.urlInput..setEditText(constants.VI_LOGIN_URL)#.setPlaceholderText(constants.VI_LOGIN_URL)
        self.urlInput.setEditable(True)
        #Login field
        self.loginLabel = QLabel()
        self.loginLabel.setText(constants.VI_LOGIN_USER_LABEL)
        
        self.loginInput = QLineEdit()
        self.loginInput.setText(constants.VI_LOGIN_USER)
        
        #Password field
        self.passwordLabel = QLabel()
        self.passwordLabel.setText(constants.VI_LOGIN_PASSWORD_LABEL)
        
        self.passwordInput = QLineEdit()
        self.passwordInput.setEchoMode(QLineEdit.Password)
       
        #Button
        self.loginButton = QPushButton(constants.VI_LOGIN_BUTTON_LABEL, self)
        self.loginButton.clicked.connect(self.clickLoginMethod)
    
        self.groupLayout.addWidget(self.urlLabel, 0, 0, 1, 1)
        self.groupLayout.addWidget(self.urlInput, 0, 1, 1, 1)
  
        self.groupLayout.addWidget(self.loginLabel, 1, 0, 1, 1)
        self.groupLayout.addWidget(self.loginInput, 1, 1, 1, 1)
        self.groupLayout.addWidget(self.passwordLabel, 2, 0, 1, 1)
        self.groupLayout.addWidget(self.passwordInput, 2, 1, 1, 1)  
        self.groupLayout.addWidget(self.loginButton, 3, 1, 1, 1)
        
        self.centralwidgetLayout.addWidget(self.groupWidget)
        with open('vitools.ini','a+') as f:
            pass
        with open('vitools.ini','r') as f:
            self.urldata=f.read().splitlines()
            self.urlInput.addItems(self.urldata)
        if not len(self.urldata):
            self.urlInput.addItems([constants.VI_LOGIN_URL])
        
    def clickLoginMethod(self):

        self.baseURL=self.urlInput.currentText().strip()
        self.username=self.loginInput.text().strip()
        self.password=self.passwordInput.text().strip()
        
        # self.baseURL="https://dcask.visiology.su"
        # self.username="admin"
        # self.password="Og4u3gj76"
        
        if self.baseURL=='' or self.username=='' or self.password=='':
            return
        
        if self.baseURL[-1]=='/':
            self.baseURL=self.baseURL[:-1]
        
        self.accept()
    def saveURL(self):
        if self.baseURL not in self.urldata:
            print(self.baseURL,self.urldata)
            with open('vitools.ini','a') as f:
                f.writelines([self.baseURL+'\n'])