# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 19:21:05 2023

@author: dcask
"""

import constants
import viplatform
from PyQt5.QtWidgets import QTextEdit, QFormLayout, QLabel, QCheckBox, QScrollArea,QGroupBox
from PyQt5.QtCore import Qt

class ViLicenseTab(QScrollArea):
    def __init__(self, parent): 
        super(QScrollArea, self).__init__(parent) 
        
        # self.widgetLayout= QVBoxLayout()
        self.groupBox = QGroupBox(self)
        self.setWidget(self.groupBox)
        # self.widgetLayout.addWidget(self.groupBox)
        self.formLayout = QFormLayout(self.groupBox)
        # self.groupBox.setLayout(self.formLayout)
        # self.scroll_area = QScrollArea()
        self.setWidgetResizable(True)
        # self.scroll_area.setWidget(self.groupBox)
        # self.setFixedHeight(200)
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

        # self.setLayout(self.formLayout)
        # GET https://example.visiology.su/admin/api/generalSettings
    # def resizeEvent(self, event):
    #     print("win",self.window().frameGeometry().height())
    #     print("scroll",self.window().frameGeometry().height())
    #     # self.groupBox.setFixedHeight(self.window().frameGeometry().height())
    #     # self.setFixedHeight(self.window().frameGeometry().height())
    #     # self.setMaximumHeight(self.window().frameGeometry().height())
    #     # self.setGeometry(self.window().frameGeometry())
    #     # self.update() 
    #     # self.resize(self.window().size())
    #     super().resizeEvent(event)
    
    def init(self):
        m=viplatform.visiology.license
        l=viplatform.visiology.usedLicenses
        
        self.adminUsers.setText(str(l["Администратор"])+constants.VI_LICENSE_LIMIT_LABEL+str(m['adminsNumber']))
        self.editorUsers.setText(str(l["Редактор"])+constants.VI_LICENSE_LIMIT_LABEL+str(m["editorsNumber"]))
        self.sfUsers.setText(str(l["Оператор ввода"])+constants.VI_LICENSE_LIMIT_LABEL+str(m["dcUsersNumber"]))
        self.otherUsers.setText(str(l["Остальные пользователи"])+constants.VI_LICENSE_LIMIT_LABEL+str(m["otherUsersNumber"]))
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