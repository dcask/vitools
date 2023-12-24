# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 13:57:47 2023

@author: dcask
"""

import constants
import viplatform
import viutils
# import urllib.request
import zipfile
import os
import shutil
from github import Github
from PyQt5.QtWidgets import QWidget,  QVBoxLayout, QLabel, QGridLayout
from PyQt5.QtWidgets import QPushButton, QLineEdit, QTreeView, QComboBox

from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread

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
def prepareDataFromGit(s, res, filename) -> dict:
    path=s.split('/')
    root=path.pop(0)
    if root not in res: res[root]={}
    if len(path)>0: 
        res[root]=prepareDataFromGit('/'.join(path),res[root],filename)
        parent_path=filename.split(root)[0]
        if parent_path!='': 
            res[root]['special_data']=parent_path+'/'+root
        else:
            res[root]['special_data']=root
    else:
        res[root]=filename
    return res
def prepareDataFromPlatform(elem_list) -> dict:
    res={}
    for elem in elem_list:
        if len(elem['children'])>0:
            res[elem['name']]=prepareDataFromPlatform(elem['children'])
        else:
            res[elem['name']]=elem['guid']
    return res
    
#-----------------------------------------------------------------------------
class ViDashboardsExport(QWidget):
    def __init__(self, parent): 
        super(QWidget, self).__init__(parent) 
        
        self.finished = pyqtSignal()
        self.catcherror = pyqtSignal(str)
        
        self.centralwidgetLayout = QVBoxLayout(self)
        
        self.groupWidget = QWidget(self)
        self.groupLayout = QGridLayout(self.groupWidget)
        
        self.apitokenLabel = QLabel()
        self.apitokenLabel.setText(constants.VI_EXPORT_KEY_LABEL)
        self.apiKey = QLineEdit()
        self.apiKey.setText("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")
        self.connectButton = QPushButton(constants.VI_IMPORT_CONNECT_BUTTON_LABEL)
        self.connectButton.clicked.connect(self.onClickConnect)
        
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
        
        self.treeViewPlatform = QTreeView(self)
        self.treeViewGit = QTreeView(self)
        self.treeViewGit.clicked.connect(self.onClickGitTree)
        
        self.exportButton = QPushButton(constants.VI_EXPORT_BUTTON_LABEL, self)
        self.exportButton.clicked.connect(self.onClickUpload)
        
        self.importButton = QPushButton(constants.VI_IMPORT_BUTTON_LABEL, self)
        self.importButton.clicked.connect(self.onClickDownload)
        
        self.groupLayout.addWidget(self.apitokenLabel,      0, 0, 1, 1)
        self.groupLayout.addWidget(self.apiKey,             0, 1, 1, 6)
        self.groupLayout.addWidget(self.connectButton,      0, 7, 1, 1)
        
        self.groupLayout.addWidget(self.repoGroup,          1, 0, 1, 2)
        self.groupLayout.addWidget(self.branchGroup,        1, 2, 1, 2)
        
        self.groupLayout.addWidget(self.prefixLabel,        1, 4, 1, 1)
        self.groupLayout.addWidget(self.prefix,             1, 5, 1, 3)
        
        self.groupLayout.addWidget(self.treeViewPlatform,   2, 0, 2, 4)
        self.groupLayout.addWidget(self.treeViewGit,        2, 4, 2, 4)
        
        self.groupLayout.addWidget(self.exportButton,       4, 0, 1, 4)
        self.groupLayout.addWidget(self.importButton,       4, 4, 1, 4)
        self.centralwidgetLayout.addWidget(self.groupWidget)
        # self.importButton.setEnabled(False)
        # self.exportButton.setEnabled(False)  
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
            item = self.model.itemFromIndex(index)
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
        pass
    def connectThread(self):
        api_token = self.apiKey.text()
        self.git = Github(api_token)
        self.exportButton.setEnabled(True)
        repos=self.git.get_user().get_repos()
        self.repoCombo.clear()
        self.repoCombo.addItems([str(i).replace('Repository(full_name="','').replace('")','') for i in repos])
        
    def onClickConnect(self):
        
        # self.loader= viutils.LoadingGif(self)
        # self.thread = QThread()
        # self.worker = viutils.WorkerLoki()
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
        self.connectThread()
        self.preparePlatformDashboardTree()
#----------------------------------------------------------------------------=
    def onRepoChanged(self):
        repo = self.repoCombo.currentText()
        if repo!='':
            self.repo = self.git.get_repo(repo)
            branches = self.repo.get_branches()
            self.branchCombo.clear()
            self.branchCombo.addItems([str(i).replace('Branch(name="','').replace('")','') for i in branches])
            self.modelGit=create_model(self.getFromGit(),"GitHub")
            self.treeViewGit.setModel(self.modelGit)
            root = self.modelGit.invisibleRootItem()
            for item in self.iterItems(root):
                if not item.hasChildren():
                    item.setCheckable(True)
                    item.setCheckState(Qt.Unchecked)
 #----------------------------------------------------------------------------=                   
    def getFromGit(self):

        all_files = []
        contents = self.repo.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(self.repo.get_contents(file_content.path))
            else:
                file = file_content
                filename=str(file).replace('ContentFile(path="','').replace('")','')
                if "name.txt" in filename:
                    filecontent=file.decoded_content.decode()
                    all_files.append(filename.replace('name.txt',filecontent))
        p={}
        for file in all_files:
           p=prepareDataFromGit(file,p, file)
        return p
#-----------------------------------------------------------------------------
    def preparePlatformDashboardTree(self):
        payload={"QueryType":"GetDashboardList+Query"}
        
        ok,response = viplatform.visiology.sendJSON('POST','/corelogic/api/query',
                                                        viplatform.visiology.headers, payload)
        if ok:
            dashboards=prepareDataFromPlatform(response.json()['result']['treeItems'])
            self.modelPlatform=create_model(dashboards,"Платформа")
            self.treeViewPlatform.setModel(self.modelPlatform)
            root = self.modelPlatform.invisibleRootItem()
            for item in self.iterItems(root):
                if not item.hasChildren():
                    item.setCheckable(True)
                    item.setCheckState(Qt.Unchecked)
            
#-----------------------------------------------------------------------------
    def onClickDownload(self):
        self.get_checked()
    def onClickUpload(self):
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
        self.uploadLocalFolder()
#------------------------------------------------------------------------------        
    def uploadLocalFolder(self):
        
        all_files = []
        git_prefix = self.prefix.text()
        repo_branch = self.branchCombo.currentText()
        contents = self.repo.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(self.repo.get_contents(file_content.path))
            else:
                file = file_content
                all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))
        
        for root, subdirs, files in os.walk(constants.VI_EXPORT_PATH):
                  
            for filename in files:
                file_path = os.path.join(root, filename)

                with open(file_path, 'r', encoding="utf-8" ) as f:
                    content = f.read()
                
                # Upload to github
                
                git_file = git_prefix+os.path.basename(root)+'/'+ filename
                if git_file in all_files:
                    contents = self.repo.get_contents(git_file)
                    self.repo.update_file(contents.path, "committing dashboards", 
                                          content, contents.sha, branch=repo_branch)
                else:
                    self.repo.create_file(git_file, "committing dashboards", 
                                          content, branch=repo_branch)
