# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 23:34:28 2023

@author: dcask
"""
import requests
import constants
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtGui
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def throwError(message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("Error")
    msg.setInformativeText(message)
    msg.setWindowTitle("Error")
    msg.setWindowIcon(QtGui.QIcon(constants.img))
    msg.exec_()
    
def throwInfo(message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText("Done")
    msg.setInformativeText(message)
    msg.setWindowTitle("Done")
    msg.setWindowIcon(QtGui.QIcon(constants.img))
    msg.exec_()

def checkPlatform(url):
        response = requests.get(url+'/viqube/version', verify=False)
        return response.ok
    
def getToken(url,strUser,strPassword):
    token=''
    apiVersion=''
    payload = f"grant_type=password&scope=openid+profile+email+roles+viqube_api+viqubeadmin_api+core_logic_facade+dashboards_export_service+script_service+migration_service_api+data_collection&response_type=id_token+token&username={strUser}&password={strPassword}"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "authorization": "Basic cHVibGljX3JvX2NsaWVudDpAOVkjbmckXXU+SF4zajY="
    }
    try:
        response = requests.request("GET", url+'/viqube/version', verify=False)
        if response.status_code == 200:
            apiVersion=response.json()['apiPartial']
        response = requests.request("POST", url+'/idsrv/connect/token', data=payload, headers=headers, verify=False)
        if response.status_code == 200:
            token = response.json()['access_token']
        else:
           throwError(response.text)
    except Exception as e:
        throwError(str(e))
    return token,apiVersion

def getAllRoles(url, token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer "+token
    }
    roleList = []
    try:
        response = requests.request("GET", url+'/admin/api/allRoles', headers=headers, verify=False)
        roles = response.json()
        for role in roles:
            if not role['IsBuiltIn']:
                roleList.append(role['Name'])
    except Exception as e:
        throwError(str(e))
    
    #roleList.append('Публичный доступ')
    return roleList
# def setRole(url, token, roleName, dbList):
#     payload = {
#         "role": roleName,
#         "databases": dbList
#     }
#     headers = {
#         "Content-Type": "application/json",
#         "X-API-VERSION": apiVersion,
#         "Authorization": "Bearer "+token
#     }
#     try:
#         response = requests.request("PUT", url+'/viqube/accessrights/roledb', json=payload, headers=headers, verify=False)
#         if response.status_code!=200:
#             throwError(response.text)
#         else:
#             throwInfo('Успешно')
#     except Exception as e:
#         throwError(str(e))
    
# def getDatabases(url, token):
#     headers = {
#         "Content-Type": "application/json",
#         "X-API-VERSION": apiVersion,
#         "Authorization": "Bearer "+token
#     }
#     databases = []
#     try:
#         response = requests.request("GET", url+'/viqube/databases', headers=headers, verify=False)
#         dbs = response.json()
#         for db in dbs:
#             databases.append(db['name'])
#     except Exception as e:
#         throwError(str(e))
#     return databases
