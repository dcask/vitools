# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 22:30:40 2023

@author: dcask
"""

import constants
import viplatform
from github import Github
from json import load
import zipfile
import os
import shutil
import base64 
from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie, QIcon
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot as Slot


#------------------------------------------------------------------------------
def loadIniFile()->dict:
    data={}
    with open('vitools.json', 'a+') as f:
        pass
    with open('vitools.json','r') as f:
        try:
            data=load(f)
        except :
            pass
    return data
#------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------
def throwError(message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("Error")
    msg.setInformativeText(message) 
    msg.setWindowTitle("Error")
    msg.setWindowIcon(QIcon(constants.VI_WINDOW_ICON_PATH))
    msg.exec_()
#------------------------------------------------------------------------------    
def throwInfo(message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText("Done")
    msg.setInformativeText(message)
    msg.setWindowTitle("Done")
    msg.setWindowIcon(QIcon(constants.VI_WINDOW_ICON_PATH))
    msg.exec_()
#--------------------------------CLASS WORKER ---------------------------------    
    
class WorkerGit(QObject):
    finished = pyqtSignal()
    catcherror = pyqtSignal(str)
    gotRepos = pyqtSignal()
    initted = pyqtSignal()
    gotRepoBranch = pyqtSignal()
    gotFiles = pyqtSignal()
    filesUploaded =pyqtSignal()
    filesDownloaded =pyqtSignal()
#------------------------------------------------------------------------------
    def __init__(self): 
        super(QObject, self).__init__()
#------------------------------------------------------------------------------
    @Slot(str)    
    def init(self, key):
        self.repos=[]
        
        try:
            self.git = Github(key)
            self.initted.emit()
        except Exception as e:
            throwError(str(e))
#------------------------------------------------------------------------------
    @Slot()        
    def getRepos(self):
        try:
            self.repos=self.git.get_user().get_repos()
        except Exception as e:
            throwError(str(e))
        self.gotRepos.emit()
#------------------------------------------------------------------------------        
    @Slot(str)
    def getRepoBranch(self, s):
        try:
            self.repo = self.git.get_repo(s)
            self.branches = self.repo.get_branches()
        except Exception as e:
            throwError(str(e))
        self.gotRepoBranch.emit()
#------------------------------------------------------------------------------        
    @Slot()
    def getFiles(self):
        all_files = []
        try:
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
            self.files={}
            for file in all_files:
                self.files=prepareDataFromGit(file,self.files, file)
            self.gotFiles.emit()
        except Exception as e:
            throwError(str(e))
#------------------------------------------------------------------------------    
    @Slot(str,str, str)
    def uploadFiles(self,git_prefix,repo_branch, commit_comment):
        all_files = []
        try:
            print('prefix', git_prefix,repo_branch)
            if git_prefix!='':
                if git_prefix[-1]!='/' : git_prefix+='/'
    
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

                    git_file = git_prefix+os.path.basename(root)+'/'+ filename
                    if git_file in all_files:
                        contents = self.repo.get_contents(git_file)
                        self.repo.update_file(contents.path, commit_comment, 
                                              content, contents.sha, branch=repo_branch)
                    else:
                        self.repo.create_file(git_file, commit_comment, 
                                              content, branch=repo_branch)
            self.filesUploaded.emit()
        except Exception as e:
            throwError(str(e))
#------------------------------------------------------------------------------            
    @Slot(list,str)
    def downloadFiles(self, filenames, branch):
        try:
            shutil.rmtree(constants.VI_IMPORT_PATH)
        except OSError as e:
            throwError(str(e))
        try:
            for f in filenames:
                
                zipname=f['data'].split('/')[-2]
                path=f['data'].replace(f['name'],'')

                gitFile=path+'dashboards.json'
                content_encoded = self.repo.get_contents(gitFile, ref=branch).content
                content = base64.b64decode(content_encoded)
                filenameDash=constants.VI_IMPORT_PATH+'\\'+zipname+'\\'+'dashboards.json'
                os.makedirs(os.path.dirname(filenameDash), exist_ok=True)
                with open(filenameDash, 'wb') as f:
                    f.write(content)

                gitFile=path+'__header.json'
                content_encoded = self.repo.get_contents(gitFile, ref=branch).content
                content = base64.b64decode(content_encoded)
                filenameHeader=constants.VI_IMPORT_PATH+'\\'+zipname+'\\'+'__header.json'
                with open(filenameHeader, 'wb') as f:
                    f.write(content)
                filename=constants.VI_IMPORT_PATH+'\\'+zipname+'\\'+zipname+'.zip'
                with zipfile.ZipFile(filename, 'a') as zipf:
                    zipf.write(filenameDash, 'dashboards.json')
                    zipf.write(filenameHeader, '__header.json')
            self.filesDownloaded.emit()
        except Exception as e:
            throwError(str(e))
# -----------------------class-------------------------------------------------        
class WorkerUser(QObject):
    finished = pyqtSignal()
    catcherror = pyqtSignal(str)
#------------------------------------------------------------------------------    
    def run(self):

        if viplatform.visiology.checkPlatform():
            viplatform.visiology.getUsers()
        if viplatform.visiology.hasError:
            self.catcherror.emit(viplatform.visiology.errorText) 
        self.finished.emit()
#---------------------class---------------------------------------------------
class WorkerToken(QObject):
    finished = pyqtSignal()
    catcherror = pyqtSignal(str)
#------------------------------------------------------------------------------
    def run(self):

        if viplatform.visiology.checkPlatform():
            viplatform.visiology.getToken()
        if viplatform.visiology.hasError:
            self.catcherror.emit(viplatform.visiology.errorText) 
        self.finished.emit()
#------------------------class-------------------------------------------------
class WorkerLicence(QObject):
    finished = pyqtSignal()
    catcherror = pyqtSignal(str)

    def run(self):

        if viplatform.visiology.checkPlatform():
            viplatform.visiology.getLicense()
        if viplatform.visiology.hasError:
            self.catcherror.emit(viplatform.visiology.errorText) 
        self.finished.emit()
#---------------class----------------------------------------------------------
class WorkerLoki(QObject):
    finished = pyqtSignal()
    catcherror = pyqtSignal(str)
#------------------------------------------------------------------------------
    def run(self):

        if viplatform.visiology.checkPlatform():
            viplatform.visiology.getDashboards()
            viplatform.visiology.getLokiDashboardRequests()
        if viplatform.visiology.hasError:
            self.catcherror.emit(viplatform.visiology.errorText) 
        self.finished.emit()
#------------------class------------------------------------------------------        
class LoadingGif(QWidget): 
#------------------------------------------------------------------------------
    def __init__(self, parent=None):
        super(QWidget, self).__init__(viplatform.visiology.windowCentralWidget)#
        self.setFixedSize(50,50)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)

        geo = self.geometry()
        geo.moveCenter(viplatform.visiology.windowCentralWidget.geometry().center())
        self.setGeometry(geo)
        self.started=True

        self.label_animation = QLabel(self)
        self.movie = QMovie(constants.VI_TABPANEL_LOADER) 
        self.label_animation.setMovie(self.movie) 
        self.startAnimation() 
        self.show()
#------------------------------------------------------------------------------  
    def startAnimation(self):
        self.started=True
        self.movie.start() 
#------------------------------------------------------------------------------
    def pauseAnimation(self):
        self.movie.stop() 
        self.hide()
#------------------------------------------------------------------------------        
    def stopAnimation(self): 
        self.started=False
        self.movie.stop()
        self.close()