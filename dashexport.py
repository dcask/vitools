# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 13:57:47 2023

@author: dcask
"""

import constants
import viplatform
# import urllib.request
import zipfile
import os
import shutil
from github import Github
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget,  QVBoxLayout, QLabel, QGridLayout, QPushButton, QLineEdit, QTreeView
from PyQt5.QtWidgets import QCheckBox,  QScrollArea, QSpacerItem
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

# class TreeModel(QStandardItemModel):
#     def __init__(self, parent=None):
#         super(TreeModel, self).__init__(parent)
#         self.get_contents()

#     def get_contents(self):
#         self.clear()
#         contents = [
#             '|Base|character|Mike|body',
#             '|Base|character|John',
#             '|Base|camera'
#         ]

#         for content in contents:
#             parent = self.invisibleRootItem()
#             for word in content.split("|")[1:]:
#                 for i in range(parent.rowCount()):
#                     item = parent.child(i) 
#                     if item.text() == word:
#                         it = item
#                         break
#                 else:
#                     it = QtGui.QStandardItem(word)
#                     parent.setChild(parent.rowCount(), it)
#                 parent = it

def add_items_to_model(parent, elements):
    for key, value in elements.items():
        item = QStandardItem(key)
        parent.appendRow(item)
        if isinstance(value, dict) and value:
            add_items_to_model(item, value)

def create_model(data):
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(['Иерархия'])
    add_items_to_model(model.invisibleRootItem(), data)
    return model
def rec(s, res) -> dict:
    path=s.split('/')
    root=path.pop(0)
    if root not in res: res[root]={}
    if len(path)>0: res[root]=rec('/'.join(path),res[root])
    return res
# app = QApplication([])

# Структура данных, которую хотим отобразить
# data = {
#     'Пункт 1': {},
#     'Пункт 2': {
#         'Подпункт 2.1': {},
#         'Подпункт 2.2': {
#             'Подпункт 2.2.1': {},
#         },
#     },
#     'Пункт 3': {
#         'Подпункт 3.1': {},
#     },
# }

# Создание модели и заполнение данными
# model = create_model(data)
class ViDashboardsExport(QWidget):
    def __init__(self, parent): 
        super(QWidget, self).__init__(parent) 
        self.centralwidgetLayout = QVBoxLayout(self)
        
        self.groupWidget = QWidget(self)
        self.groupLayout = QGridLayout(self.groupWidget)
        self.apitokenLabel = QLabel()
        self.apitokenLabel.setText("GIT API KEY")
        self.apiKey = QLineEdit()
        self.apiKey.setText("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")
        self.checkBoxList=[]

        self.scrollAreaPlatform = QScrollArea(self)
        self.scrollAreaPlatform.setWidgetResizable(True)
        self.scrollAreaPlatformWidget = QWidget()

        self.scrollAreaPlatformWidgetLayout = QVBoxLayout(self.scrollAreaPlatformWidget)
        self.scrollAreaPlatformWidgetLayout.addItem(QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        self.scrollAreaPlatform.setWidget(self.scrollAreaPlatformWidget)
        
        # self.scrollAreaGit = QScrollArea(self)
        self.tree_view = QTreeView(self)
        
        self.tree_view.expandAll()  # Раскрыть все узлы
        # self.scrollAreaGit.setWidgetResizable(True)
        # self.scrollAreaGitWidget = QWidget()

        # self.scrollAreaGitWidgetLayout = QVBoxLayout(self.scrollAreaGitWidget)
        # self.scrollAreaGitWidgetLayout.addItem(QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        
        # self.scrollAreaGitWidgetLayout.addItem(self.tree_view)
        # self.scrollAreaGit.setWidget(self.scrollAreaGitWidget)
        
        self.groupLayout.addWidget(self.apitokenLabel, 0, 0, 1, 1)
        self.groupLayout.addWidget(self.apiKey, 0, 1, 1, 1)
        self.groupLayout.addWidget(self.scrollAreaPlatform, 1, 0, 2, 1)
        # self.groupLayout.addWidget(self.scrollAreaGit, 1, 1, 2, 1)
        self.groupLayout.addWidget(self.tree_view, 1, 1, 2, 1)
        
        self.centralwidgetLayout.addWidget(self.groupWidget)
        #self.centralwidgetLayout.addWidget(self.scrollArea)
        
        self.exportButton = QPushButton(constants.VI_EXPORT_BUTTON_LABEL, self)
        self.exportButton.clicked.connect(self.onClickUpload)

        # self.exportButton.setEnabled(False)
        
        self.importButton = QPushButton(constants.VI_IMPORT_BUTTON_LABEL, self)
        self.importButton.clicked.connect(self.onClickDownload)

        # self.importButton.setEnabled(False)
        
        self.groupLayout.addWidget(self.exportButton, 3, 0, 1, 1)
        self.groupLayout.addWidget(self.importButton, 3, 1, 1, 1)
    
    def get_checked(self):
        checked = self.model.match(
            self.model.index(0, 0), Qt.CheckStateRole,
            Qt.Checked, -1,
            Qt.MatchExactly | Qt.MatchRecursive)
        for index in checked:
            item = self.model.itemFromIndex(index)
            print(item.parent().text())
    
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
    
    def init(self):
        for i in self.checkBoxList: i.deleteLater()
        self.checkBoxList=[]
        dbs = viplatform.visiology.dashboards
        for dashboard in dbs:
            cb=QCheckBox(self)
            cb.setText(str(dashboard) +'->'+str(dbs[dashboard]))
            count = self.scrollAreaPlatformWidgetLayout.count() - 1
            self.scrollAreaPlatformWidgetLayout.insertWidget(count, cb)
            self.checkBoxList.append(cb)
        # self.linkButton.setEnabled(True)
        self.model=create_model(self.getFromGit())
        self.tree_view.setModel(self.model)
        root = self.model.invisibleRootItem()
        print(root.text())
        for item in self.iterItems(root):
            
            if not item.hasChildren():
                item.setCheckable(True)
                item.setCheckState(Qt.Unchecked)

        # self.getFromGit()
        
    def getFromGit(self):
        api_token = self.apiKey.text()
        # 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
        g = Github(api_token)

        GITHUB_REPO = 'dashboards'
        repo = g.get_user().get_repo(GITHUB_REPO)
        all_files = []
        
        contents = repo.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                file = file_content
                filename=str(file).replace('ContentFile(path="','').replace('")','')
                if "name.txt" in filename:
                    filecontent=file.decoded_content.decode()
                    
                    all_files.append(filename.replace('name.txt',filecontent))
                # elif "__header.json" not in filename and "dashboards.json" not in filename:
                #     all_files.append(filename)
        p={}
        for file in all_files:
           p=rec(file,p)
        return p
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
        for chb in self.checkBoxList:
            if chb.isChecked():
                gid,name=chb.text().split('->')
                payload["dashboardsGuidList"]=[gid]
                
                filename=constants.VI_EXPORT_PATH+'\\'+chb.text().split('->')[0]+'\\'+chb.text().split('->')[0]+'.zip'
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
                    s.write(name)
                os.remove(filename)
        self.git()
        
    def git(self):
        
        api_token = self.apiKey.text()
        # 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
        g = Github(api_token)

        GITHUB_REPO = 'dashboards'
        repo = g.get_user().get_repo(GITHUB_REPO)
        all_files = []
        git_prefix = 'test2_34/'
        
        contents = repo.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                file = file_content
                all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))
        
        for root, subdirs, files in os.walk(constants.VI_EXPORT_PATH):
                  
            for filename in files:
                file_path = os.path.join(root, filename)
                # print(os.path.basename(root)) 
                # print('\t- file %s (full path: %s)' % (filename, file_path))
    
                with open(file_path, 'r', encoding="utf-8" ) as f:
                    content = f.read()
                
                # Upload to github
                
                git_file = git_prefix+os.path.basename(root)+'/'+ filename
                if git_file in all_files:
                    contents = repo.get_contents(git_file)
                    repo.update_file(contents.path, "committing files", content, contents.sha, branch="main")
                    print(git_file + ' UPDATED')
                else:
                    repo.create_file(git_file, "committing files", content, branch="main")
                    print(git_file + ' CREATED')