# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 13:57:47 2023

@author: dcask
"""

import constants
import viplatform
import viutils
import zipfile
import os
import shutil
from PyQt5.QtWidgets import QWidget,  QVBoxLayout, QLabel, QGridLayout
from PyQt5.QtWidgets import QPushButton, QLineEdit, QTreeView, QComboBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread

#-----------------------------------------------------------------------------
def add_items_to_model(parent, elements):
    for key, value in elements.items():
        item = QStandardItem(key)
        parent.appendRow(item)
        if isinstance(value, str) and value:
            item.setData(value)
        if isinstance(value, dict) and value:
            if 'special_data' in value:
                item.setData(value['special_data'])
                del value['special_data']
            add_items_to_model(item, value)
#-----------------------------------------------------------------------------
def create_model(data, name):
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels([name])
    add_items_to_model(model.invisibleRootItem(), data)
    return model
#-----------------------------------------------------------------------------
def prepareDataFromPlatform(elem_list) -> dict:
    res={}
    for elem in elem_list:
        if len(elem['children'])>0:
            res[elem['name']]=prepareDataFromPlatform(elem['children'])
        else:
            res[elem['name']]=elem['guid']
    return res
    
#--------------------------  class -------------------------------------------
class ViDashboardsExport(QWidget):
    commandLoadfiles= pyqtSignal()
    commandGetRepos = pyqtSignal()
    commandGetRepoBranch = pyqtSignal(str)
    commandInit = pyqtSignal(str)
    commandUploadFiles = pyqtSignal(str,str,str)
    commandDownloadFiles = pyqtSignal(list,str)
#-----------------------------------------------------------------------------    
    def __init__(self, parent): 
        super(QWidget, self).__init__(parent) 

        self.centralwidgetLayout = QVBoxLayout(self)
        
        self.groupWidget = QWidget(self)
        self.groupLayout = QGridLayout(self.groupWidget)
        
        self.apitokenLabel = QLabel()
        self.apitokenLabel.setText(constants.VI_EXPORT_KEY_LABEL)
        self.apiKey = QLineEdit()
        # self.apiKey.setText("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")
        #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
        self.connectButton = QPushButton(constants.VI_IMPORT_CONNECT_BUTTON_LABEL)
        self.connectButton.clicked.connect(self.onClickConnect)
        self.connectButton.setStyleSheet('QPushButton {background-color: #dd556d}')
        self.repoGroup = QWidget()
        self.repoGroupLayout =QVBoxLayout(self.repoGroup)
        self.repoLabel = QLabel()
        self.repoLabel.setText(constants.VI_EXPORT_REPO_LABEL)
        self.repoCombo = QComboBox()
        self.repoCombo.currentTextChanged.connect(self.onRepoChanged)
        self.repoGroupLayout.addWidget(self.repoLabel)
        self.repoGroupLayout.addWidget(self.repoCombo)

        self.branchGroup = QWidget()
        self.branchGroupLayout =QVBoxLayout(self.branchGroup)
        self.branchLabel = QLabel()
        self.branchLabel.setText(constants.VI_EXPORT_BRANCH_LABEL)
        self.branchCombo = QComboBox()
        self.branchGroupLayout.addWidget(self.branchLabel)
        self.branchGroupLayout.addWidget(self.branchCombo)
        
        self.prefixLabel = QLabel()
        self.prefixLabel.setText(constants.VI_EXPORT_PREFIX_LABEL)
        self.prefix = QLineEdit()
        self.prefixDeaultStyle = self.prefix.styleSheet() #original saved
        self.prefix.textChanged.connect(self.onchangePrefix)

        self.treeViewPlatform = QTreeView(self)
        self.treeViewGit = QTreeView(self)
        self.treeViewGit.clicked.connect(self.onClickGitTree)
        
        self.exportButton = QPushButton(constants.VI_EXPORT_BUTTON_LABEL, self)
        self.exportButton.clicked.connect(self.onClickUpload)
        
        self.commentLabel = QLabel()
        self.commentLabel.setText(constants.VI_EXPORT_COMMENT_LABEL)
        self.comment = QLineEdit()
        self.comment.setText(constants.VI_EXPORT_COMMENT_TEXT)
                            
        self.importButton = QPushButton(constants.VI_IMPORT_BUTTON_LABEL, self)
        self.importButton.clicked.connect(self.onClickDownload)
        
        self.exportButton.setStyleSheet('QPushButton {background-color: #f5b25c}')
        self.importButton.setStyleSheet('QPushButton {background-color: #76b6f9}')
        
        self.groupLayout.addWidget(self.apitokenLabel,      0, 0, 1, 1)
        self.groupLayout.addWidget(self.apiKey,             0, 1, 1, 6)
        self.groupLayout.addWidget(self.connectButton,      0, 7, 1, 1)
        
        self.groupLayout.addWidget(self.repoGroup,          1, 0, 1, 2)
        self.groupLayout.addWidget(self.branchGroup,        1, 2, 1, 2)
        
        self.groupLayout.addWidget(self.prefixLabel,        1, 4, 1, 1, Qt.AlignRight)
        self.groupLayout.addWidget(self.prefix,             1, 5, 1, 3)
        
        self.groupLayout.addWidget(self.treeViewPlatform,   2, 0, 2, 4)
        self.groupLayout.addWidget(self.treeViewGit,        2, 4, 2, 4)
        
        self.groupLayout.addWidget(self.exportButton,       4, 0, 1, 4)
        self.groupLayout.addWidget(self.importButton,       4, 4, 1, 4)
        
        self.groupLayout.addWidget(self.commentLabel,       5, 0, 1, 1)
        self.groupLayout.addWidget(self.comment,            5, 1, 1, 3)
        
        self.centralwidgetLayout.addWidget(self.groupWidget)
          
#-----------------------------------------------------------------------------
    def closeEvent(self, event):
        self.thread.quit()
#-----------------------------------------------------------------------------
    def onClickGitTree(self, modelIndex):
        item=self.modelGit.itemFromIndex(modelIndex)
        if item.hasChildren():
            self.prefix.setText(item.data())    
#-----------------------------------------------------------------------------
    def get_checked(self, model):
        res=[]
        checked = model.match(
            model.index(0, 0), Qt.CheckStateRole,
            Qt.Checked, -1,
            Qt.MatchExactly | Qt.MatchRecursive)
        for index in checked:
            item = model.itemFromIndex(index)
            res.append({'name':item.text(), 'data':item.data()})
        return res
#-----------------------------------------------------------------------------    
    def iterItems(self, root):
        if root is not None:
            stack = [root]
            while stack:
                parent = stack.pop(0)
                for row in range(parent.rowCount()):
                    for column in range(parent.columnCount()):
                        child = parent.child(row, column)
                        yield child
                        if child.hasChildren():
                            stack.append(child)
#-----------------------------------------------------------------------------                            
    def init(self):
        if viplatform.visiology.hasError: return
        self.thread = QThread()
        self.worker = viutils.WorkerGit()
        self.worker.moveToThread(self.thread)
        self.thread.finished.connect(self.thread.deleteLater)
        # self.finished.connect(self.thread.quit)
        self.worker.gotRepos.connect(self.loadReposCombo)
        
        self.worker.initted.connect(self.connectThread)
        self.worker.gotRepoBranch.connect(self.loadRepoBranch)
        self.worker.gotFiles.connect(self.prepareGitDashboardTree)
        self.worker.filesUploaded.connect(self.onRepoChanged)

        self.worker.filesDownloaded.connect(self.uploadLocalFolder2Platform)
        self.worker.catcherror.connect(viutils.throwError)
        self.commandInit.connect(self.worker.init)
        self.commandLoadfiles.connect(self.worker.getFiles)
        self.commandGetRepos.connect(self.worker.getRepos)
        self.commandGetRepoBranch.connect(self.worker.getRepoBranch)
        self.commandUploadFiles.connect(self.worker.uploadFiles)
        self.commandDownloadFiles.connect(self.worker.downloadFiles)
   
        self.apiKey.setText(viplatform.visiology.githubkey)

        self.thread.start()

#-----------------------------thread ------------------------------------------
    def loadReposCombo(self):
        try:
            repos=self.worker.repos # here list
            self.repoCombo.clear()
            self.repoCombo.addItems([str(i).replace('Repository(full_name="','').replace('")','') for i in repos])
            viplatform.visiology.saveIniFile({'githubkey':self.apiKey.text()})
            self.preparePlatformDashboardTree()
        except Exception as e:
            viutils.throwError(str(e))
        self.loader.stopAnimation()
#-----------------------------------------------------------------------------        
    def connectThread(self):

        self.exportButton.setEnabled(True)
        self.commandGetRepos.emit()
#-----------------------------------------------------------------------------
    def onClickConnect(self): 
        self.loader= viutils.LoadingGif(self)
        self.commandInit.emit(self.apiKey.text())
#-----------------------------------------------------------------------------
    def prepareGitDashboardTree(self):
        
        
        self.modelGit=create_model(self.worker.files,constants.VI_IMPORT_TREE_LABEL) #here dict
        self.treeViewGit.setModel(self.modelGit)
        root = self.modelGit.invisibleRootItem()
        for item in self.iterItems(root):
            if not item.hasChildren():
                item.setCheckable(True)
                item.setCheckState(Qt.Unchecked)
        self.treeViewGit.expandAll()
        self.loader.stopAnimation()
        
#------------------------------thread-----------------------------------------
    def loadRepoBranch(self):
        try:
            branches = self.worker.branches #here list
            self.branchCombo.clear()
            self.branchCombo.addItems([str(i).replace('Branch(name="','').replace('")','') for i in branches])
            if self.loader.started:
                self.loader.stopAnimation()
            self.loader= viutils.LoadingGif(self.groupWidget)
            
            self.commandLoadfiles.emit()
        except Exception as e:
            viutils.throwError(str(e))
        
#----------------------------------------------------------------------------=
    def onRepoChanged(self):
        
        repo = self.repoCombo.currentText()
        if repo!='':
           
            self.commandGetRepoBranch.emit(repo)
 #-----------------------------------------------------------------------------
    def preparePlatformDashboardTree(self):
        payload={"QueryType":"GetDashboardList+Query"}
        
        ok,response = viplatform.visiology.sendJSON('POST','/corelogic/api/query',
                                                        viplatform.visiology.headers, payload)
        if ok:
            dashboards=prepareDataFromPlatform(response.json()['result']['treeItems'])
            self.modelPlatform=create_model(dashboards,constants.VI_EXPORT_TREE_LABEL)
            self.treeViewPlatform.setModel(self.modelPlatform)
            root = self.modelPlatform.invisibleRootItem()
            for item in self.iterItems(root):
                if not item.hasChildren():
                    item.setCheckable(True)
                    item.setCheckState(Qt.Unchecked)
            self.treeViewPlatform.expandAll()
            
#-----------------------------------------------------------------------------
    def onClickDownload(self):
        if self.loader.started:
            self.loader.stopAnimation()
        self.loader= viutils.LoadingGif(self.groupWidget)
        d=self.get_checked(self.modelGit) 
        self.commandDownloadFiles.emit(d, self.branchCombo.currentText())
#--------------------------------------------------------------------------
    def onClickUpload(self):
        try:
            if self.prefix.text()=='':
                self.prefix.setStyleSheet("border: 1px solid red;") #changed
                return
            if self.loader.started:
                self.loader.stopAnimation()
            self.loader= viutils.LoadingGif(self.groupWidget)
            payload={"dashboardsGuidList":[],
                    "dataSources":[],
                    "dimensions": [],
                    "imagesGuidList": [],
                    "measureGroups": [],
                    "tables": []
                    }
            try:
                shutil.rmtree(constants.VI_EXPORT_PATH)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))
            dashList = self.get_checked(self.modelPlatform)
            for d in dashList:
                
                payload["dashboardsGuidList"]=[d['data']]
                
                filename=constants.VI_EXPORT_PATH+'\\'+d['data']+'\\'+d['data']+'.zip'
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                print(payload)
                ok_ver,response = viplatform.visiology.sendJSON('POST','/migration/export',
                                                                viplatform.visiology.headers, payload)     
                data = response.content
                with open(filename, 'wb') as s:
                    s.write(data)
                with zipfile.ZipFile(filename, 'r') as zip_ref:
                    zip_ref.extractall(os.path.dirname(filename))
                with open(os.path.dirname(filename)+'/name.txt', 'w',encoding="utf-8") as s:
                    s.write(d['name'])
                os.remove(filename)
            if len(dashList)>0:
                            
                self.commandUploadFiles.emit(self.prefix.text(),self.branchCombo.currentText(),
                                             self.comment.text())
        except Exception as e:
            viutils.throwError(str(e))

#------------------------------------------------------------------------------        
    def uploadLocalFolder2Platform(self):
        
        for root, subdirs, files in os.walk(constants.VI_IMPORT_PATH):
                  
            for filename in files:
                file_path = os.path.join(root, filename)
                name, file_extension = os.path.splitext(file_path)
                if file_extension=='.zip':
                    
                    with open(file_path, 'rb') as fobj:
                        data=fobj.read()
                        ok,response = viplatform.visiology.sendFile('/migration/import',data)
        self.preparePlatformDashboardTree()              
        self.loader.stopAnimation()
#-----------------------------------------------------------------------------
    def onchangePrefix(self):
        self.prefix.setStyleSheet(self.prefixDeaultStyle)