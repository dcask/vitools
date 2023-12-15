# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 21:07:53 2023

@author: dcask
"""
import constants
from dbaccess import ViDbAccessTab
from vilicense import ViLicenseTab
from userTab import ViUserTab
from apitool import ViApiTab
from lokitab import ViLokiTab
from PyQt5.QtWidgets import QTabWidget

class ViTabPanel(QTabWidget): 
    def __init__(self, parent): 
        super(QTabWidget,self).__init__(parent) 

        self.setTabPosition(QTabWidget.North)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.tab4 = ViDbAccessTab(self) 
        self.tab2 = ViUserTab(self) 
        self.tab3 = ViLicenseTab(self) 
        self.tab1 = ViApiTab(self) 
        self.tab5 = ViLokiTab(self) 
        self.resize(600, 400) 

        self.addTab(self.tab1, constants.VI_TABPANEL_TAB1_NAME) 
        self.addTab(self.tab2, constants.VI_TABPANEL_TAB2_NAME) 
        self.addTab(self.tab3, constants.VI_TABPANEL_TAB3_NAME)
        self.addTab(self.tab4, constants.VI_TABPANEL_TAB4_NAME)
        self.addTab(self.tab5, constants.VI_TABPANEL_TAB5_NAME)
        
    def init(self):
        self.tab1.init()
        self.tab2.init()
        self.tab3.init()
        self.tab4.init()
        self.tab5.init()
    
