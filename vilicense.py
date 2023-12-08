# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 19:21:05 2023

@author: dcask
"""

import constants
import viplatform
from PyQt5.QtWidgets import QWidget,  QFormLayout, QLabel

class ViLicenseTab(QWidget):
    def __init__(self, parent): 
        super(QWidget, self).__init__(parent) 
        
        self.formLayout = QFormLayout(self)
        
        self.adminUsers = QLabel()
        self.adminUsers.setText('0')
        
        self.editorUsers = QLabel()
        self.editorUsers.setText('0')
        
        self.sfUsers = QLabel()
        self.sfUsers.setText('0')
        
        self.otherUsers = QLabel()
        self.otherUsers.setText('0')
        
        self.totalUsers = QLabel()
        self.totalUsers.setText('0')
        
        self.formLayout.addRow(constants.VI_LICENSE_ADMIN_LABEL, self.adminUsers)
        self.formLayout.addRow(constants.VI_LICENSE_EDITOR_LABEL, self.editorUsers)
        self.formLayout.addRow(constants.VI_LICENSE_SF_LABEL, self.sfUsers)
        self.formLayout.addRow(constants.VI_LICENSE_OTHER_LABEL, self.otherUsers)
        self.formLayout.addRow(constants.VI_LICENSE_TOTAL_LABEL, self.totalUsers)

        self.setLayout(self.formLayout)
      
        
    def init(self):
        m=viplatform.visiology.license
        l=viplatform.visiology.usedLicenses
        
        self.adminUsers.setText(str(l["Администратор"])+constants.VI_LICENSE_LIMIT_LABEL+str(m['adminsNumber']))
        self.editorUsers.setText(str(l["Редактор"])+constants.VI_LICENSE_LIMIT_LABEL+str(m["editorsNumber"]))
        self.sfUsers.setText(str(l["Оператор ввода"])+constants.VI_LICENSE_LIMIT_LABEL+str(m["dcUsersNumber"]))
        self.otherUsers.setText(str(l["Остальные пользователи"])+constants.VI_LICENSE_LIMIT_LABEL+str(m["otherUsersNumber"]))
        self.totalUsers.setText(str(l["Всего"]))