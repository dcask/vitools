# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 23:54:40 2023

@author: dcask
"""

import constants
import viplatform
import viutils
# from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget,QTableView, QLabel, QGridLayout, QLineEdit, QPushButton
from PyQt5.QtWidgets import QAbstractItemView,QHeaderView
from PyQt5.QtWidgets import QComboBox, QFileDialog
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QAbstractTableModel, QThread
from PyQt5.QtCore import QVariant, pyqtSlot, QRegExp, QItemSelection, QItemSelectionModel
from PyQt5.QtGui import QColor, QBrush

class TableModel(QAbstractTableModel):
    def __init__(self, data, headers):
        super().__init__()
        self._data = data
        self.hheaders = headers
    #---------- check data ----------
    def data(self, index, role= Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        if role == Qt.CheckStateRole:
            value = self._data[index.row()][index.column()]
            
            if isinstance(value, bool):
                if value:
                    return Qt.Checked
                else:
                    return Qt.Unchecked

        if role == Qt.DisplayRole:
            value = self._data[index.row()][index.column()]
            if isinstance(value, bool):
                return ('Нет','Да')[value]
            return value
        if role == Qt.BackgroundRole:
            row = index.row()
            odd = QColor(255,255,255)
            even = QColor(235,235,235)
            return (QBrush(even),QBrush(odd))[row %2 ==0]
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
           
    #---------- model row count -------------------    
    def rowCount(self, index):
        return len(self._data)
    def sort(self, Ncol, order):
        self.layoutAboutToBeChanged.emit()
        self._data = self._data.sort_values(self.headers[Ncol],
                                          ascending=order == Qt.AscendingOrder)
        self.layoutChanged.emit()
    # def setData(self, index, value, role=Qt.EditRole):
    #     if not index.isValid():
    #         return False
    #     if role == Qt.CheckStateRole and index.column() == 0:
    #         self._data[index.row()][index.column()] = not self._data[index.row()][index.column()]
    #         self.dataChanged.emit(index, index, [role])
    #         return True
    #     return False
    
    # def flags(self, index):
    #     if not index.isValid():
    #         return Qt.NoItemFlags
    #     if index.column() == 0 :
    #         return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
    #     return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def columnCount(self, index):
        return len(self._data[0])
    
    def headerData(self, section, orientation, role):           
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.hheaders[section]
        return QVariant()
    
    def item(self, row, column):
        return QVariant()

class ViUserTab(QWidget):
    def __init__(self, parent): 
        super(QWidget, self).__init__(parent)
        
        self.view           = QTableView()
        self.view.setWordWrap(True)
        self.view.setSortingEnabled(True)
        self.lineEdit       = QLineEdit()
        self.comboBox       = QComboBox()
        self.label          = QLabel()
        self.label.setText(constants.VI_USER_FIND_LABEL)
        self.totalLabel          = QLabel()
        self.totalLabel.setText(constants.VI_USER_TOTAL_LABEL)
        self.total          = QLabel()
        
        #buttons
        self.loadXLSbutton = QPushButton(constants.VI_USER_LOAD,self)
        self.saveXLSbutton = QPushButton(constants.VI_USER_SAVE,self)
        self.selectAllbutton = QPushButton(constants.VI_USER_SELECT,self)
        self.unselectAllbutton = QPushButton(constants.VI_USER_DESELECT,self)
        self.deactivatebutton = QPushButton(constants.VI_USER_DEACTIVATE,self)
        self.removeSelectedbutton = QPushButton(constants.VI_USER_DELETE,self)
        self.saveXLSbutton.clicked.connect(self.clickSave)
        self.loadXLSbutton.clicked.connect(self.clickLoad)
        
        self.selectAllbutton.clicked.connect(self.clickSelect)
        self.unselectAllbutton.clicked.connect(self.clickUnSelect)
        self.removeSelectedbutton.clicked.connect(self.clickRemove)
        self.deactivatebutton.clicked.connect(self.clickUnBlock)
        
        self.loadXLSbutton.setStyleSheet('QPushButton {background-color: #f9c076}')
        self.saveXLSbutton.setStyleSheet('QPushButton {background-color: #f5b25c}')
        self.selectAllbutton.setStyleSheet('QPushButton {background-color: #76b6f9}')
        self.unselectAllbutton.setStyleSheet('QPushButton {background-color: #a9ccf1}')
        self.deactivatebutton.setStyleSheet('QPushButton {background-color: #95f18b}')
        self.removeSelectedbutton.setStyleSheet('QPushButton {background-color: #dd556d}')
        
        self.gridLayout = QGridLayout(self)
        self.gridLayout.addWidget(self.label,0,0, 1,1, Qt.AlignRight)
        self.gridLayout.addWidget(self.comboBox,0,1,1,1)
        self.gridLayout.addWidget(self.lineEdit,0,2,1,4)
        
        self.gridLayout.addWidget(self.view,                 1, 0, 1, 6)
        self.gridLayout.addWidget(self.totalLabel,           2, 0, 1, 1)
        self.gridLayout.addWidget(self.total,                 2, 1, 1, 5)
        self.gridLayout.addWidget(self.selectAllbutton,      3, 0, 1, 1)
        self.gridLayout.addWidget(self.unselectAllbutton,    3, 1, 1, 1)                          
        self.gridLayout.addWidget(self.removeSelectedbutton, 3, 2, 1, 1)
        self.gridLayout.addWidget(self.loadXLSbutton,        3, 3, 1, 1)
        self.gridLayout.addWidget(self.saveXLSbutton,        3, 4, 1, 1)
        self.gridLayout.addWidget(self.deactivatebutton,     3, 5, 1, 1)
        
        
        # self.centralwidgetLayout.addWidget(self.centralwidget)
        self.setLayout(self.gridLayout)
        
        self.view.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.view.setSelectionMode(QAbstractItemView.MultiSelection)
        self.verticalHeader = self.view.verticalHeader()
    
    @pyqtSlot(str)
    def on_lineEdit_textChanged(self, text):
        search = QRegExp(    text,
                                    Qt.CaseInsensitive,
                                    QRegExp.RegExp
                                    )
        self.proxy.setFilterRegExp(search)
        self.total.setText(str(self.view.model().rowCount())+constants.VI_USER_OF_LABEL+str(len(viplatform.visiology.userList)))
    # @pyqtSlot(int)
    # def on_view_horizontalHeader_sectionClicked(self, logicalIndex):  
    #     self.proxy.sort(logicalIndex,-1)
    @pyqtSlot(int)
    def on_comboBox_currentIndexChanged(self, index):
        self.proxy.setFilterKeyColumn(index)
    
    def init(self):
        
        self.view.reset()

        translate={'UserName':'Логин', 'useLdap':'LDAP', 'GivenName':'Имя',
                   'FamilyName':'Фамилия', 'MiddleName':'Отчество', 'Email':'Email',
                   'Roles':'Роли', 'IsActive':'Лицензия',
                   #'LockoutEndDate':'LockoutEndDate',
                   'IsBuiltIn':'Встроенно', 
                   'IsBlocked':'Блок', 'LastLogin':'Последний вход', 'Created':'Создан'
                   }
        headers=[]
        data=[]
        for u in viplatform.visiology.userList:
            if not u["IsInfrastructure"]:
                u['Roles']=', '.join(u['Roles'])
                d=[]
                headers=[]
                for key in u:
                    if key in translate:
                        headers.append(translate[key])
                        if key in ['LastLogin', 'Created']:
                            d.append(str(u[key]).replace('T',' ').replace('Z',''))
                        else:
                            d.append(u[key])
                data.append(d)
        # print(data)
        # headers = [translate[key] for key in viplatform.visiology.userList[0]]
        # print(headers)
        self.model = TableModel(data,headers)
        
        # self.model.setHorizontalHeaderLabels([viplatform.visiology.userList[0][key] for key in viplatform.visiology.userList[0]])
        # self.model = QStandardItemModel(self)
        # for rowName in range(3*5):
        #     self.model.invisibleRootItem().appendRow(
        #         [   QStandardItem("row {0} col {1}".format(rowName, column))    
        #             for column in range(3)
        #             ]
        #         )
        
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.view.setModel(self.proxy)
        self.comboBox.addItems(headers)
        # print(headers)
        self.lineEdit.textChanged.connect(self.on_lineEdit_textChanged)
        self.comboBox.currentIndexChanged.connect(self.on_comboBox_currentIndexChanged)
        
        self.horizontalHeader = self.view.horizontalHeader()
        self.horizontalHeader.setSectionsClickable(True)
        # self.horizontalHeader.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        # self.horizontalHeader.setSectionResizeMode(6, QHeaderView.ResizeToContents) #Stretch)
        # self.horizontalHeader.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        # self.horizontalHeader.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        # self.horizontalHeader.setSectionResizeMode(9, QHeaderView.ResizeToContents)
        self.horizontalHeader.setStyleSheet("QHeaderView::section \
                                        {\
                                             background-color: #abe7ab; \
                                             color: black; \
                                              border-top: 0px; \
                                              border-bottom:1px inset #91eb91;\
                                             }")
        self.total.setText(str(self.view.model().rowCount())+constants.VI_USER_OF_LABEL+str(len(viplatform.visiology.userList)))
        
        # self.resizeRowsToContents()
        
        self.verticalHeader.setSectionResizeMode( QHeaderView.ResizeToContents)
        for index,value in enumerate(headers):
            # if value in ['LDAP','Лицензируется']:
                self.horizontalHeader.setSectionResizeMode(index, QHeaderView.ResizeToContents)
        self.horizontalHeader.setSectionResizeMode(6, QHeaderView.Stretch)
        # self.horizontalHeader.setSectionResizeMode(0, QHeaderView.Stretch)
        # self.horizontalHeader.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        # self.horizontalHeade.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        # self.horizontalHeader.sectionClicked.connect(self.on_view_horizontalHeader_sectionClicked)
        # displayHeaders=['UserName', 'useLdap', 'GivenName', 'FamilyName', 'MiddleName', 'Email', 'Roles', 'IsActive', 'LockoutEndDate', 'AccessFailedCount', 'IsBlocked', 'LastLogin', 'Created']
        # for i, h in enumerate(headers):
        #     if h not in displayHeaders:
        #         self.view.hideRow(i)
        #         print (h)
        # self.view.resizeRowsToContents()
        self.view.resizeColumnsToContents()
        # self.view.update()
        # self.view.repaint()
#------------------- save------------------------
    def clickSave(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,constants.VI_USER_SAVEAS_LABEL,""," Text Files (*.xlsx)", options=options)
        if fileName:
            if fileName[:-5] !='.xlsx': fileName+='.xlsx'
            viplatform.visiology.saveExcel(fileName, "Sheet1")
#------------------- load------------------------
    def clickLoad(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,constants.VI_USER_LOADAS_LABEL, "","excel (*.xlsx)", options=options)
        if fileName:
            if not viplatform.visiology.loadExcel(fileName, "Sheet1"):
                viutils.throwError(viplatform.visiology.errorText)
            # else:
            #     viutils.throwInfo("Загружено")
        
        self.refresh()
        self.total.setText(str(self.view.model().rowCount())+constants.VI_USER_OF_LABEL+str(len(viplatform.visiology.userList)))
#------------------- Select all------------------------
    def clickSelect(self):
        index1 = self.view.model().index(0, 0)
        index2 = self.view.model().index(self.view.model().rowCount()-1, 0)
        itemSelection = QItemSelection(index1, index2)
        self.view.selectionModel().select(itemSelection, QItemSelectionModel.Rows | QItemSelectionModel.Select)
        self.view.setFocus()
#------------------- UnSelect all------------------------
    def clickUnSelect(self):
        self.view.clearSelection()
        self.view.setFocus()

#------------------- Remove selected users------------------------
    def clickRemove(self):
        indices = self.view.selectionModel().selectedRows()
        f=True
        error_val=''
        for index in sorted(indices):
            val = str(index.data(role=Qt.DisplayRole))
            if not viplatform.visiology.removeUser(val):
                error_val+=val+";"
                f=False
        if not f:
            # viutils.throwInfo("Успешно")
        # else:
            viutils.throwError(error_val +" "+ viplatform.visiology.errorText)
        self.refresh()
        self.total.setText(str(self.view.model().rowCount())+constants.VI_USER_OF_LABEL+str(len(viplatform.visiology.userList)))
#------------------- Remove selected users------------------------
    def clickUnBlock(self):
        indices = self.view.selectionModel().selectedRows()
        error_val=''
        f=True
        for index in indices:
            val = str(index.data(role=Qt.DisplayRole))
            if not viplatform.visiology.deactivateUser(val):
                error_val+=val+";"
                f=False
        
        if not f:
        #     viutils.throwInfo("Успешно")
        # else:
            viutils.throwError(error_val +" "+ viplatform.visiology.errorText)
            
        self.refresh()
        self.total.setText(str(self.view.model().rowCount())+constants.VI_USER_OF_LABEL+str(len(viplatform.visiology.userList)))
#--------------------refresh---------------------------
    def refresh(self):
        self.loader= viutils.LoadingGif(self)
        self.thread = QThread()
        self.worker = viutils.WorkerUser()
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
        self.thread.finished.connect(
            lambda: self.init()
        )
        # self.view.resizeColumnsToContents()
#---------------------------------------
    # def resizeRowsToContents(self):
        
    #     # self.verticalHeader.setSectionResizeMode( QHeaderView.Stretch)
    #     for row in range(self.view.model().rowCount()):
    #             hint = self.view.sizeHintForRow(row)
    #             self.verticalHeader.resizeSection(row, hint)