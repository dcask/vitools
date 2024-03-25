# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 23:15:16 2023

@author: dcask
"""


import constants
import viplatform
import viutils
from pandas import DataFrame
from PyQt5.QtWidgets import QWidget,QTableView, QLabel, QGridLayout, QLineEdit, QPushButton
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QComboBox, QFileDialog, QSpinBox
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QAbstractTableModel, QThread
from PyQt5.QtCore import QVariant, pyqtSlot, QRegExp#, QModelIndex
from PyQt5.QtGui import QColor, QBrush

from re import search
from json import loads 
#--------------------------------- class -------------------------------------
class LokiTableModel(QAbstractTableModel):
    def __init__(self, data, headers):
        super().__init__()
        self._data = data
        self.hheaders = headers
#-------------------------- check data ---------------------------------------
    def data(self, index, role= Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        if role == Qt.DisplayRole:
            value = self._data[index.row()][index.column()]
            return value
        if role == Qt.BackgroundRole:
            row = index.row()
            odd = QColor(255,255,255)
            even = QColor(235,235,235)
            return (QBrush(even),QBrush(odd))[row %2 ==0]
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
           
#---------------------- model row count --------------------------------------    
    def rowCount(self, index):
        return len(self._data)
#-----------------------------------------------------------------------------
    def sort(self, Ncol, order):
        self.layoutAboutToBeChanged.emit()
        self._data = self._data.sort_values(self.headers[Ncol],
                                          ascending=order == Qt.AscendingOrder)
        self.layoutChanged.emit()
#-----------------------------------------------------------------------------
    def columnCount(self, index):
        return len(self.hheaders)
    
#-----------------------------------------------------------------------------    
    def headerData(self, section, orientation, role):           
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.hheaders[section]
        return QVariant()
#-----------------------------------------------------------------------------    
    def item(self, row, column):
        return QVariant()
#-------------------------class ----------------------------------------------
class ViLokiTab(QWidget):
    def __init__(self, parent): 
        super(QWidget, self).__init__(parent)
        self.lokiKey       = QLineEdit()
        self.lineEdit       = QLineEdit()
        self.since      = QSpinBox()
        self.since.setValue(24)
        
        self.view           = QTableView()
        self.view.setSortingEnabled(True)
        
        self.lineEdit       = QLineEdit()
        self.comboBox       = QComboBox()
        self.label          = QLabel()
        self.label.setText(constants.VI_USER_FIND_LABEL)
        
        self.labelKey         = QLabel()
        self.labelKey.setText(constants.VI_LOKI_KEY_LABEL)
        self.labelSince         = QLabel()
        self.labelSince.setText(constants.VI_LOKI_SINCE_LABEL)
        self.totalLabel          = QLabel()
        self.totalLabel.setText(constants.VI_USER_TOTAL_LABEL)
        self.total          = QLabel()
        
        #buttons
        self.saveXLSbutton = QPushButton(constants.VI_LOKI_SAVE,self)
        self.saveXLSbutton.clicked.connect(self.clickSave)
        
        self.refreshButton = QPushButton(constants.VI_LOKI_REFRESH,self)
        self.refreshButton.clicked.connect(self.refresh)
       
        self.saveXLSbutton.setStyleSheet('QPushButton {background-color: #f5b25c}')
        self.refreshButton.setStyleSheet('QPushButton {background-color: #76b6f9}')
        self.gridLayout = QGridLayout(self)
       
        self.gridLayout.addWidget(self.label,                0, 0, 1, 1, Qt.AlignRight)
        self.gridLayout.addWidget(self.comboBox,             0, 1, 1, 1)
        self.gridLayout.addWidget(self.lineEdit,             0, 2, 1, 4)
        
        self.gridLayout.addWidget(self.view,                 1, 0, 1, 6)
        self.gridLayout.addWidget(self.labelKey,             2, 0, 1, 1)
        self.gridLayout.addWidget(self.lokiKey,              2, 1, 1, 2)
        self.gridLayout.addWidget(self.labelSince,           2, 3, 1, 1)
        self.gridLayout.addWidget(self.since,                2, 4, 1, 1)
        self.gridLayout.addWidget(self.refreshButton,        2, 5, 1, 1)
        
        self.gridLayout.addWidget(self.totalLabel,           3, 0, 1, 1)
        self.gridLayout.addWidget(self.total,                3, 1, 1, 1)
        self.gridLayout.addWidget(self.saveXLSbutton,        3, 5, 1, 1)
        self.setLayout(self.gridLayout)
        

        self.verticalHeader = self.view.verticalHeader()
#-----------------------------------------------------------------------------
    @pyqtSlot(str)
    def on_lineEdit_textChanged(self, text):
        search_str = QRegExp(    text,
                                    Qt.CaseInsensitive,
                                    QRegExp.RegExp
                                    )
        self.proxy.setFilterRegExp(search_str)
        self.total.setText(str(self.view.model().rowCount()))
#-----------------------------------------------------------------------------
    @pyqtSlot(int)
    def on_comboBox_currentIndexChanged(self, index):
        self.proxy.setFilterKeyColumn(index)
#-----------------------------------------------------------------------------
    def init(self):
        if viplatform.visiology.hasError: return
        if self.lokiKey.text()=='':
            self.lokiKey.setText(viplatform.visiology.lokiApiKey)
        self.view.reset()
        self.loadLoki()
        self.comboBox.clear()
        headers=['Время','Дашбоард','GUID','UserName']

        self.model = LokiTableModel(self.data,headers)

        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.view.setModel(self.proxy)
        self.comboBox.addItems(headers)
        self.lineEdit.textChanged.connect(self.on_lineEdit_textChanged)
        self.comboBox.currentIndexChanged.connect(self.on_comboBox_currentIndexChanged)
    
        self.horizontalHeader = self.view.horizontalHeader()
        self.horizontalHeader.setSectionsClickable(True)
        self.horizontalHeader.setStyleSheet("QHeaderView::section \
                                        {\
                                             background-color: #abe7ab; \
                                             color: black; \
                                              border-top: 0px; \
                                              border-bottom:1px inset #91eb91;\
                                             }")
        
        for index,value in enumerate(headers):
              self.horizontalHeader.setSectionResizeMode(index, QHeaderView.ResizeToContents)
        self.total.setText(str(self.view.model().rowCount()))
#------------------- save------------------------
    def clickSave(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,constants.VI_USER_SAVEAS_LABEL,"",
                                                  " Text Files (*.xlsx)", options=options)
        if fileName:
            if fileName[:-5] !='.xlsx': fileName+='.xlsx'
            self.saveLokiExcel(fileName, "Sheet1")
#--------------------refresh---------------------------
    def refresh(self):
        viplatform.visiology.lokiApiKey=self.lokiKey.text()
        self.loader= viutils.LoadingGif(self)
        self.thread = QThread()
        self.worker = viutils.WorkerLoki('dash')
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.catcherror.connect(viutils.throwError)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        self.thread.finished.connect(
            lambda: self.loader.stopAnimation()
        )
        # self.worker.catcherror.connect(
        #     lambda: self.loader.stopAnimation()
        # )
        self.thread.finished.connect(
            lambda: self.init()
        )

#-------------------------- save excel -------------------------
    def saveLokiExcel(self, excel_filename, sheet_name):
        df = DataFrame(self.data)
        try:
            df.to_excel(excel_filename, sheet_name=sheet_name, index=False, engine='openpyxl')
        except Exception as e:
            viutils.throwError(str(e))
#------------------- load from loki -----------------------------------------
    def loadLoki(self):
        self.data=[]
        if self.lokiKey.text()=='':
            return

        if len(viplatform.visiology.dash_views):
            regtemplate=r'{.*}'
            for r in viplatform.visiology.dash_views["data"]["result"]:
                if len(viplatform.visiology.dash_views["data"]["result"])>0:
                    for value in r["values"]:
                        v=loads(value[1])
                        d = search(regtemplate,v['log'])
                        if d:
                            p=d.group()[1:-1]
                            result = dict((a.strip(), b.strip()[1:-1])  
                                      for a, b in (element.split(': ')  
                                                  for element in p.split(', ')))
                            self.data.append([v['time'].replace('T',' ').replace('Z',''),
                                              viplatform.visiology.dashboards[result['DashboardGuid']],
                                              result['DashboardGuid'],result['UserLogin']])
                            
