# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 21:29:14 2023

@author: dcask
"""

import constants
import viplatform
from viutils import throwError,throwInfo
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget,  QVBoxLayout, QLabel, QGridLayout, QPushButton
from PyQt5.QtWidgets import QCheckBox, QComboBox, QScrollArea, QSpacerItem
from PyQt5.QtCore import Qt

class ViDbAccessTab(QWidget):
    def __init__(self, parent): 
        super(QWidget, self).__init__(parent) 
        self.centralwidgetLayout = QVBoxLayout(self)
        
        self.groupWidget = QWidget(self)
        self.groupLayout = QGridLayout(self.groupWidget)
        
        #Role List
        self.checkBoxList=[]
        self.rolesLabel = QLabel()
        self.rolesLabel.setText(constants.VI_ACCESS_ROLES_LABEL)
        
        self.combo_box = QComboBox()
        self.combo_box.currentTextChanged.connect(self.on_combobox_changed)
        #DB list
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidget = QWidget()

        self.scrollAreaWidgetLayout = QVBoxLayout(self.scrollAreaWidget)
        self.scrollAreaWidgetLayout.addItem(QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        self.scrollArea.setWidget(self.scrollAreaWidget)
        
        self.groupLayout.addWidget(self.rolesLabel, 0, 0, 1, 1, Qt.AlignRight)
        self.groupLayout.addWidget(self.combo_box, 0, 1, 1, 1)
        self.groupLayout.addWidget(self.scrollArea, 2, 0, 2, 2)
        
        self.centralwidgetLayout.addWidget(self.groupWidget)
        #self.centralwidgetLayout.addWidget(self.scrollArea)
        
        self.linkButton = QPushButton(constants.VI_ACCESS_BUTTON_LABEL, self)
        self.linkButton.clicked.connect(self.clickLinkMethod)

        self.linkButton.setEnabled(False)
        self.groupLayout.addWidget(self.linkButton, 5, 1, 1, 1)
        
    def clickLinkMethod(self):  
        
        dbs=[]
        for chb in self.checkBoxList:
            if chb.isChecked():
                dbs.append(chb.text())
                
        if not viplatform.visiology.setRole(self.combo_box.currentText(), dbs):
            throwError(constants.VI_TABPANEL_ERROR_LINK+viplatform.visiology.errorText)
        else:
            throwInfo("Успешно")
        
        
    def init(self):
        for i in self.checkBoxList: i.deleteLater()
        self.checkBoxList=[]
        self.combo_box.clear()
        self.combo_box.addItems(viplatform.visiology.getAllRoles())

        dbs=viplatform.visiology.getDatabases()
        # print(dbs)
        
        for db in dbs:
            cb=QCheckBox(self)
            cb.setText(db)
            count = self.scrollAreaWidgetLayout.count() - 1
            self.scrollAreaWidgetLayout.insertWidget(count, cb)
            self.checkBoxList.append(cb)
        self.linkButton.setEnabled(True)
        
    def on_combobox_changed(self):
        t=self.combo_box.currentText()
        for role in viplatform.visiology.db_roles:
            if t==role['role']:
                for d in role['databases']:
                    for c in self.checkBoxList:
                        if c.text()==d['dataBase']:
                            c.setChecked(True)