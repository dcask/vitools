# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 22:19:05 2023

@author: dcask
"""

import constants
import viplatform
from pandas import DataFrame

from viutils import throwError
from json import loads, dumps, dump, load
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QLineEdit, QPushButton
from PyQt5.QtWidgets import QComboBox, QTextEdit, QFileDialog
from PyQt5.QtWidgets import QPlainTextEdit, QAction, QMenu
from PyQt5.QtCore import Qt
#------------------------------------------------------------------------------
class ViApiTab(QWidget):
    def __init__(self, parent): 
        super(QWidget, self).__init__(parent)
        
        self.comboBox       = QComboBox()
        self.comboBox.setEditable(True)
        self.comboBox.currentTextChanged.connect(self.on_combobox_changed)
        self.comboType       = QComboBox()
        self.comboType.addItems(['GET','POST','PUT','DELETE'])

        self.endpointEdit   = QLineEdit()
        self.labelToken  = QLabel()
        self.labelToken.setText(constants.VI_API_TOKEN_LABEL)
        self.tokenEdit= QTextEdit()
        self.labelHeaders  = QLabel()
        self.labelHeaders.setText(constants.VI_API_HEADERS_LABEL)
        self.headerEdit=QTextEdit()
        self.labelBody  = QLabel()
        self.labelBody.setText(constants.VI_API_BODY_LABEL)
        self.bodyEdit=QPlainTextEdit()
        self.labelOutput  = QLabel()
        self.labelOutput.setText(constants.VI_API_OUTPUT_LABEL)
        self.outputEdit= QTextEdit()
        
        self.outputEdit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.outputEdit.customContextMenuRequested.connect(self.context_menu)
        self.export = QAction(self.tr('xls'), self)
        self.export.triggered.connect(self.exportAction)
        
        self.tokenEdit.setReadOnly(True)
        self.outputEdit.setReadOnly(True)

        self.refreshButton = QPushButton(constants.VI_API_REFRESH_BUTTON)

        self.sendButton = QPushButton(constants.VI_API_SEND_BUTTON)
        self.saveButton = QPushButton(constants.VI_API_SAVE_BUTTON)
        
        self.refreshButton.clicked.connect(self.clickRefresh)
        self.sendButton.clicked.connect(self.clickSend)
        self.saveButton.clicked.connect(self.clickSave)
        self.refreshButton.setStyleSheet('QPushButton {background-color: #a9ccf1}')
        self.sendButton.setStyleSheet('QPushButton {background-color: #95f18b}')
        self.saveButton.setStyleSheet('QPushButton {background-color: #f5b25c}')
        self.gridLayout = QGridLayout(self)
        
        self.gridLayout.addWidget(self.comboType,               0, 0)
        
        self.gridLayout.addWidget(self.endpointEdit,            1, 0)
        self.gridLayout.addWidget(self.labelToken,              2, 0)
        self.gridLayout.addWidget(self.tokenEdit,               3, 0)
        self.gridLayout.addWidget(self.labelHeaders,            4, 0)
        self.gridLayout.addWidget(self.headerEdit,              5, 0)
        self.gridLayout.addWidget(self.labelBody,               6, 0)
        self.gridLayout.addWidget(self.bodyEdit,                7, 0)
        
        self.gridLayout.addWidget(self.comboBox,                0, 1, 1, 1)
        self.gridLayout.addWidget(self.saveButton,              0, 2, 1, 1)
        self.gridLayout.addWidget(self.sendButton,              1, 1, 1, 1)
        self.gridLayout.addWidget(self.labelOutput,             2, 1, 1, 1)
        self.gridLayout.addWidget(self.outputEdit,              3, 1, 5, 3)

        
        self.gridLayout.addWidget(self.refreshButton,           1, 2, 1, 1)
        
        self.gridLayout.setColumnStretch(0, 2)
        self.gridLayout.setColumnStretch(1, 1)
        
        self.gridLayout.setRowStretch(0, 1)
        self.gridLayout.setRowStretch(1, 1)
        self.gridLayout.setRowStretch(2, 1)
        self.gridLayout.setRowStretch(3, 2)
        self.gridLayout.setRowStretch(4, 1)
        self.gridLayout.setRowStretch(5, 2)
        self.gridLayout.setRowStretch(6, 1)
        self.gridLayout.setRowStretch(7, 4)
        
        self.endpointEdit.setText("/viqube/version")
        self.setLayout(self.gridLayout)
        
        with open('vitools-data.json', 'a+') as f:
            pass
        with open('vitools-data.json','r') as f:
            try:
                items=['',]
                
                self.tooltip=load(f)
                for x in self.tooltip : items.append(x)
                self.comboBox.addItems(items)
            except :
                self.tooltip={}
        # print(self.tooltip)
#------------------------------------------------------------------------------        
    def init(self):
        if viplatform.visiology.hasError: return
        h = dict(viplatform.visiology.headers)
        h['Authorization']=h['Authorization'].replace(viplatform.visiology.userToken,"["+constants.VI_API_TOKEN_LABEL+"]")
        self.headerEdit.setText(dumps(h, indent=2))
        self.tokenEdit.setText(viplatform.visiology.userToken)
        self.bodyEdit.setPlainText("body")
#------------------------------------------------------------------------------        
    def clickRefresh(self):
        viplatform.visiology.getToken()
        self.tokenEdit.setText(str(viplatform.visiology.userToken))
#------------------------------------------------------------------------------        
    def clickSend(self):
        
        self.sendApiRequest()
#------------------------------------------------------------------------------        
    def refreshView(self):
        self.tokenEdit.setText(viplatform.visiology.userToken)   
#------------------------------------------------------------------------------        
    def sendApiRequest(self):
        
        # catcherror = pyqtSignal(str)
        data=self.grabData()
        if "CORRECT" in data:
            viplatform.visiology.timeout_value=100
            ok, response=viplatform.visiology.sendJSON(data["METHOD"],
                                                            data["ENDPOINT"],
                                                            data["HEADERS"],
                                                            data["BODY"])
            viplatform.visiology.timeout_value=10                                                
            if ok:
                string=constants.VI_API_EMPTY
                try:
                    string=dumps(response.json(), indent=2).encode('utf-8').decode('unicode_escape')
                    
                except :
                    pass
                self.outputEdit.setText(string)
                
            else:
                self.outputEdit.setText(response.text)
#------------------------------------------------------------------------------        
    def clickSave(self):
             
        data=self.grabData()
        if "CORRECT" in data:
            data['HEADERS']['Authorization']=data['HEADERS']['Authorization'].replace(viplatform.visiology.userToken,"["+constants.VI_API_TOKEN_LABEL+"]")
            name=self.comboBox.currentText().strip()
            if name=='':
                name='request'+str(len(self.tooltip))
            self.tooltip[name]=dict(data)
            self.comboBox.addItems([name])
            with open('vitools-data.json', 'w', encoding='utf-8') as f:
                dump(self.tooltip, f, ensure_ascii=False, indent=4)
#------------------------------------------------------------------------------            
    def grabData(self):
        body={}
        try:
            if self.comboType.currentText() in ['PUT','POST','DELETE']:
                body=loads(self.bodyEdit.toPlainText() )   
        except Exception as e:
            throwError(constants.VI_API_BODY_ERROR+str(e))
            return {}
        headers={}
        try:
            headers=loads(self.headerEdit.toPlainText() )   
        except Exception as e:
            throwError(constants.VI_API_HEADER_ERROR+str(e))
            return {}
        
        headers['Authorization']=headers['Authorization'].replace("["+constants.VI_API_TOKEN_LABEL+"]",viplatform.visiology.userToken)
        
        data={"METHOD":self.comboType.currentText().strip(),
              "ENDPOINT":self.endpointEdit.text().strip(),
              "HEADERS":headers,
              "BODY":body,
              "CORRECT":True}
        self.refreshView()
        return data
#------------------------------------------------------------------------------    
    def on_combobox_changed(self, value):
        if value in self.tooltip:
            data=self.tooltip[value]
            self.endpointEdit.setText(data['ENDPOINT'])
            h = dict(data['HEADERS'])
            b = dict(data['BODY'])
            h['Authorization'] = "Bearer ["+constants.VI_API_TOKEN_LABEL+"]"
            self.headerEdit.setText(dumps(h, indent=2))
            self.comboType.setCurrentText(data['METHOD'])
            self.bodyEdit.setPlainText(dumps(b, indent=2))
#------------------------------------------------------------------------------            
    def context_menu(self, pos):
       menu = QMenu(self)
       menu.addAction(self.export)
       menu.exec_(self.outputEdit.mapToGlobal(pos))
#------------------------------------------------------------------------------       
    def exportAction(self):
        
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,constants.VI_USER_SAVEAS_LABEL,""," Text Files (*.xlsx)", options=options)
        if fileName:
            if fileName[:-5] !='.xlsx': fileName+='.xlsx'
            
            df=None
            json_out=loads(self.outputEdit.toPlainText())
            if isinstance(json_out, list):
                df= DataFrame(json_out)
            if isinstance(json_out, dict):
                df = DataFrame.from_dict(loads(self.outputEdit.toPlainText()),orient="index")
            if not df.empty:
                try:
                    df.to_excel(fileName, sheet_name="Sheet1", index=False, engine='openpyxl')
                except Exception as e:
                    throwError(str(e))