# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 23:15:16 2023

@author: dcask
"""


import constants
import viplatform
import viutils
from PyQt5.QtWidgets import QWidget,QTableView, QLabel, QGridLayout, QLineEdit, QPushButton
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QAbstractTableModel, QThread
from PyQt5.QtCore import QVariant, pyqtSlot, QRegExp, pyqtSlot
from PyQt5.QtGui import QColor, QBrush

#--------------------------------- class -------------------------------------
class MonitorTableModel(QAbstractTableModel):
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
class ViMonitorTab(QWidget):
    def __init__(self, parent): 
        super(QWidget, self).__init__(parent)
        

        self.view           = QTableView()
        self.view.setSortingEnabled(True)
        self.view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.view.clicked.connect(self.onClickedRow)
        # self.view.itemSelectionChanged.connect(self.selection_changed)
        self.view.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.lineEdit       = QLineEdit()
        self.comboBox       = QComboBox()
        self.label          = QLabel()
        self.label.setText(constants.VI_USER_FIND_LABEL)
        
        self.labelMessage         = QLabel()
        self.labelMessage.setText(constants.VI_SHELL_MESSAGE_LABEL)
        self.targetComboBox       = QComboBox()
        self.message       = QLineEdit()
    
        #buttons
        self.sendButton = QPushButton(constants.VI_SHELL_SEND_BUTTON_LABEL,self)
        self.sendButton.setStyleSheet('QPushButton {background-color: #dd556d}')
        self.sendButton.clicked.connect(self.clickSendMessage)
        
        self.refreshButton = QPushButton(constants.VI_LOKI_REFRESH,self)
        self.refreshButton.setStyleSheet('QPushButton {background-color: #76b6f9}')
        self.refreshButton.clicked.connect(self.refresh)
        
        
       
        self.gridLayout = QGridLayout(self)
       
        self.gridLayout.addWidget(self.label,                0, 0, 1, 1, Qt.AlignRight)
        self.gridLayout.addWidget(self.comboBox,             0, 1, 1, 1)
        self.gridLayout.addWidget(self.lineEdit,             0, 2, 1, 4)
        
        self.gridLayout.addWidget(self.view,                 1, 0, 1, 6)
        self.gridLayout.addWidget(self.labelMessage,         2, 0, 1, 1)
        self.gridLayout.addWidget(self.targetComboBox,       2, 1, 1, 1)
        self.gridLayout.addWidget(self.message,              2, 2, 1, 3)
        self.gridLayout.addWidget(self.sendButton,           2, 5, 1, 1)
        self.gridLayout.addWidget(self.refreshButton,        3, 5, 1, 1)
        
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

        self.view.reset()
        
        self.loadMonitor()
        self.comboBox.clear()
        headers=['Id','IP','Пользователь', 'Имя дашборда', 'dashboard guid']

        self.model = MonitorTableModel(self.data,headers)

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
#------------------- Select all------------------------
    def onClickedRow(self, index=None):
        # index1 = self.view.model().index(0, 0)
        # index2 = self.view.model().index(self.view.model().rowCount()-1, 0)
        index = self.view.selectionModel().selectedRows()[0]
        val = str(index.data(role=Qt.DisplayRole))
        self.targetComboBox.setCurrentText(val)
#-----------------------------------------------------------------------------       
    def clickSendMessage(self):  
        viplatform.visiology.sendAdminMessage(self.message.text(), self.targetComboBox.currentText())
#-----------------------------------------------------------------------------
    def refresh(self):
        # viplatform.visiology.lokiApiKey=self.lokiKey.text()
        # self.loader= viutils.LoadingGif(self)
        # self.thread = QThread()
        # self.worker = viutils.WorkerLoki('ident')
        # self.worker.moveToThread(self.thread)
        # self.thread.started.connect(self.worker.run)
        # self.worker.finished.connect(self.thread.quit)
        # self.worker.finished.connect(self.worker.deleteLater)
        # self.worker.catcherror.connect(viutils.throwError)
        # self.thread.finished.connect(self.thread.deleteLater)
        # self.thread.start()
        # self.thread.finished.connect(
        #     lambda: self.loader.stopAnimation()
        # )
        # self.thread.finished.connect(
        #     lambda: self.init()
        # )
        self.init()
        pass

#------------------- load from loki -----------------------------------------
    def loadMonitor(self):
        self.targetComboBox.clear()
        self.targetComboBox.addItems(['all',])
        connections = viplatform.visiology.getConnections()
        self.data=[]
        for connection in connections:
            self.data.append([connection['client_id'],
                              connection['ip'],
                              connection['user'],
                              viplatform.visiology.dashboards[connection['dashboard'] ],
                              connection['dashboard']])
            self.targetComboBox.addItems([connection['client_id'],])
        pass
                            