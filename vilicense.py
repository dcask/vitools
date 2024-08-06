# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 19:21:05 2023

@author: dcask
"""

import constants
import viplatform
from PyQt5.QtWidgets import QTextEdit, QFormLayout, QLabel, QCheckBox, QScrollArea,QGroupBox
from PyQt5.QtCore import Qt
#------------------------------------------------------------------------------
class ViLicenseTab(QScrollArea):
    def __init__(self, parent): 
        super(QScrollArea, self).__init__(parent) 
        
        self.groupBox = QGroupBox(self)
        self.setWidget(self.groupBox)

        self.formLayout = QFormLayout(self.groupBox)

        self.setWidgetResizable(True)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.adminUsers = QLabel(self.groupBox)
        self.adminUsers.setText('0')
        
        self.editorUsers = QLabel(self.groupBox)
        self.editorUsers.setText('0')
        
        self.sfUsers = QLabel(self.groupBox)
        self.sfUsers.setText('0')
        
        self.otherUsers = QLabel(self.groupBox)
        self.otherUsers.setText('0')
        
        self.totalUsers = QLabel(self.groupBox)
        self.totalUsers.setText('0')
        self.listQWidgets=[]
        
        self.formLayout.addRow(constants.VI_LICENSE_ADMIN_LABEL, self.adminUsers)
        self.formLayout.addRow(constants.VI_LICENSE_EDITOR_LABEL, self.editorUsers)
        self.formLayout.addRow(constants.VI_LICENSE_SF_LABEL, self.sfUsers)
        self.formLayout.addRow(constants.VI_LICENSE_OTHER_LABEL, self.otherUsers)
        self.formLayout.addRow(constants.VI_LICENSE_TOTAL_LABEL, self.totalUsers)

#------------------------------------------------------------------------------    
    def init(self):
        if viplatform.visiology.hasError: return
        m=viplatform.visiology.license
        l=viplatform.visiology.usedLicenses
        print(m)
        if 'adminsNumber' in m and 'Администратор' in l:
            self.adminUsers.setText(str(l["Администратор"])+constants.VI_LICENSE_LIMIT_LABEL+str(m['adminsNumber']))
        if 'editorsNumber' in m and 'Редактор' in l:
            self.editorUsers.setText(str(l["Редактор"])+constants.VI_LICENSE_LIMIT_LABEL+str(m["editorsNumber"]))
        if 'dcUsersNumber' in m and 'Оператор ввода' in l:
            self.sfUsers.setText(str(l["Оператор ввода"])+constants.VI_LICENSE_LIMIT_LABEL+str(m["dcUsersNumber"]))
        if 'otherUsersNumber' in m and 'Остальные пользователи' in l:
            self.otherUsers.setText(str(l["Остальные пользователи"])+constants.VI_LICENSE_LIMIT_LABEL+str(m["otherUsersNumber"]))
        if 'Всего' in l:
            self.totalUsers.setText(str(l["Всего"]))
        
        ok, response = viplatform.visiology.sendRequest('GET', '/admin/api/generalSettings', viplatform.visiology.headers)
        if ok:
            r= response.json()
            for i in r:
                newwidget=None
                if isinstance(r[i], bool):
                    newwidget= QCheckBox(self)
                    newwidget.setChecked(r[i])
                    newwidget.setDisabled(True)
                else: # isinstance(r[i], list):
                    t=str(r[i])
                    if len(t)>100:
                        newwidget= QTextEdit(self)
                        newwidget.setText(t)
                    else:
                        newwidget= QLabel(self)
                        newwidget.setText(t)
                # if isinstance(r[i], list):
                self.formLayout.addRow(str(i), newwidget)