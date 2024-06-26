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
from entrancetab import ViIdentityTab
from dashexport import ViDashboardsExport
from vishell import ViShellTab
from monitor import ViMonitorTab
from PyQt5.QtWidgets import QTabWidget
#------------------------------------------------------------------------------
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
        self.tab6 = ViDashboardsExport(self)
        self.tab7 = ViIdentityTab(self)
        self.tab8 = ViShellTab(self)
        self.tab9 = ViMonitorTab(self)
        self.resize(600, 400) 

        self.addTab(self.tab1, constants.VI_TABPANEL_TAB1_NAME) 
        self.addTab(self.tab2, constants.VI_TABPANEL_TAB2_NAME) 
        self.addTab(self.tab3, constants.VI_TABPANEL_TAB3_NAME)
        self.addTab(self.tab4, constants.VI_TABPANEL_TAB4_NAME)
        self.addTab(self.tab5, constants.VI_TABPANEL_TAB5_NAME)
        self.addTab(self.tab6, constants.VI_TABPANEL_TAB6_NAME)
        self.addTab(self.tab7, constants.VI_TABPANEL_TAB7_NAME)
        self.addTab(self.tab8, constants.VI_TABPANEL_TAB8_NAME)
        self.addTab(self.tab9, constants.VI_TABPANEL_TAB9_NAME)
#----------------------------------------------------------------------------        
    def init(self):
        self.tab1.init()
        self.tab2.init()
        self.tab3.init()
        self.tab4.init()
        self.tab5.init()
        self.tab6.init()
        self.tab7.init()
        self.tab8.init()
        self.tab9.init()
#----------------------------------------------------------------------------        
    def closeEvent(self, event):
        self.tab1.close()
        self.tab2.close()
        self.tab3.close()
        self.tab4.close()
        self.tab5.close()
        self.tab6.close()
        self.tab7.close()
        self.tab8.close()
        self.tab9.close()
        event.accept()
   