# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 09:07:42 2023

@author: dcask
"""
import requests
from viutils import loadIniFile,throwError
from urllib.parse import urlencode
# import constants
from time import time
from json import load,dump, dumps
from pandas import DataFrame, read_excel
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

global errorsCounter
errorsCounter=0
#-----------------------------------------------------------------------------
def init(username,password, baseUrl) -> bool:
    global visiology
    visiology=ViPlatform()
    return visiology.init(username,password, baseUrl)
    
#------------------------------ class ----------------------------------------    
class ViPlatform():
#--------------------------------------------------------------------    
    def getError(self)-> str:
        if self.hasError:
            self.hasError=False
            return self.errorText
        return ''
#-------------------- startup init ----------------------------
    def __init__(self):
        self.baseURL=''
        self. password=''
        self.lokiApiKey=''
        self.user=''
        self.timeout_value=20
        self.clearData()
        self.windowCentralWidget=None
#------------clear data-----------------------------
    def clearData(self):  
        self.since=24
        self.userToken=''
        self.db_roles=[]
        self.apiVersion=''
        self.githubkey=''
        self.errorText=''
        self.headers={}
        self.userList=[]
        self.license={}
        self.dash_views={}
        self.dashboards = {}
        self.usedLicenses={}
        self.hasError=False
#-------------------- init ----------------------------
    def init(self, username,password, baseUrl) -> bool:
        self.password=password
        self.user=username
        self.baseURL=baseUrl
        urldata=loadIniFile()
        if self.baseURL in urldata:
            if 'LOKI' in urldata[self.baseURL]:
                self.lokiApiKey=urldata[self.baseURL]['LOKI']
            if 'githubkey' in urldata[self.baseURL]:
                self.githubkey=urldata[self.baseURL]['githubkey']
        return self.getToken()
    def show(self) -> None:
        print(self.user)
#-------------------- get access Token ----------------------------
    def getToken(self) -> bool:
        payload = {'grant_type':'password',
                   'scope':'openid profile email roles viqube_api viqubeadmin_api core_logic_facade dashboards_export_service script_service migration_service_api data_collection',
                   'response_type':'id_token token',
                   'username': self.user,
                   'password':self.password
        }
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Authorization": "Basic cHVibGljX3JvX2NsaWVudDpAOVkjbmckXXU+SF4zajY="
        }
        
        
        ok_ver,response = self.sendRequest('GET','/viqube/version', headers)
        if ok_ver:
            try:
                self.apiVersion=response.json()['apiPartial']
            except:
                pass
        ok_token,response = self.sendRequest('POST','/idsrv/connect/token',headers,payload)
        if ok_token:
            try:
                self.userToken = response.json()['access_token']
            except:
                pass
            self.headers = {
                "Content-type": "application/json",
                "X-API-VERSION": self.apiVersion,
                "Authorization": "Bearer "+self.userToken
            }
        return ok_ver and ok_token
# ----------------- check platform host ---------------------------    
    def checkPlatform(self) -> bool:
        self.hasError=False
        ok, response = self.sendRequest('GET','/viqube/version', self.headers)
        return ok
# -------------- get all roles ------------------------------------
    def getAllRoles(self) -> list:
        roleList = []
        ok, response = self.sendRequest('GET','/admin/api/allRoles',self.headers)
        if ok:
            try:
                roles = response.json()
                for role in roles:
                    if not role['IsBuiltIn']:
                        roleList.append(role['Name'])
            except:
                pass
  
        roleList.append('Публичный доступ')
        roleList.append('Все авторизованные пользователи')
        return roleList
#------------------- set Roles ----------------
    def setRole(self, roleName, dbList)-> bool:
        payload = {
            "role": roleName,
            "databases": dbList
        }
        ok, response=self.sendRequest("PUT", '/viqube/accessrights/roledb', self.headers, dumps(payload))
        self.getDatabases()
        return ok
# ----------------------------- get databases ---------------
    def getDatabases(self) -> list:
        databases = []
        ok, response = self.sendRequest('GET','/viqube/databases',self.headers)
        if ok:
            try:
                dbs = response.json()
                for db in dbs:
                    databases.append(db['name'])
            except:
                pass
        ok, response = self.sendRequest('GET','/viqube/accessrights/roledb',self.headers)
        if ok:
            try:
                self.db_roles = response.json()
            except:
                pass
        return databases
#------------------------- get license -------------------------
    def getLicense(self):
        self.license={'adminsNumber':0, 'editorsNumber':0, 'dcUsersNumber':0, 'otherUsersNumber':0 }

        ok, response = self.sendRequest('GET',"/admin/license/limits", self.headers)
        if ok:
            try:
                self.license=response.json()
            except:
                pass            
#------------------------- get users -------------------------
    def getUsers(self):
        payload={
          "columns[0][data]": "",
          "columns[0][name]": "",
          "columns[0][orderable]": "false",
          "columns[0][search][regex]": "false",
          "columns[0][search][value]": "",
          "columns[0][searchable]": "true",
          "columns[1][data]": "",
          "columns[1][name]": "",
          "columns[1][orderable]": "false",
          "columns[1][search][regex]": "false",
          "columns[1][search][value]": "",
          "columns[1][searchable]": "true",
          "columns[2][data]": "FamilyName",
          "columns[2][name]": "",
          "columns[2][orderable]": "true",
          "columns[2][search][regex]": "false",
          "columns[2][search][value]": "",
          "columns[2][searchable]": "true",
          "columns[3][data]": "GivenName",
          "columns[3][name]": "",
          "columns[3][orderable]": "true",
          "columns[3][search][regex]": "false",
          "columns[3][search][value]": "",
          "columns[3][searchable]": "true",
          "columns[4][data]": "MiddleName",
          "columns[4][name]": "",
          "columns[4][orderable]": "true",
          "columns[4][search][regex]": "false",
          "columns[4][search][value]": "",
          "columns[4][searchable]": "true",
          "columns[5][data]": "UserName",
          "columns[5][name]": "",
          "columns[5][orderable]": "true",
          "columns[5][search][regex]": "false",
          "columns[5][search][value]": "",
          "columns[5][searchable]": "true",
          "columns[6][data]": "Email",
          "columns[6][name]": "",
          "columns[6][orderable]": "true",
          "columns[6][search][regex]": "false",
          "columns[6][search][value]": "",
          "columns[6][searchable]": "true",
          "columns[7][data]": "",
          "columns[7][name]": "",
          "columns[7][orderable]": "false",
          "columns[7][search][regex]": "false",
          "columns[7][search][value]": "",
          "columns[7][searchable]": "true",
          "columns[8][data]": "",
          "columns[8][name]": "",
          "columns[8][orderable]": "false",
          "columns[8][search][regex]": "false",
          "columns[8][search][value]": "",
          "columns[8][searchable]": "true",
          "draw": "5",
          "length": "10000",
          "order[0][column]": "2",
          "order[0][dir]": "asc",
          "search[regex]": "false",
          "search[value]": "",
          "selectedRole": "Все авторизованные пользователи",
          "start": "0"
        }
        headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                 "Authorization": self.userToken}
        ok, response = self.sendRequest('POST',"/admin/api/users", headers, payload)
        if ok:
            try:
                self.userList=response.json()["data"]
            except:
                pass
            self.calculateLicenses()
                        
#----------------------- used licenses -----------------------
    def calculateLicenses(self):
        self.usedLicenses={"Администратор":0,"Редактор":0,"Оператор ввода":0}
        others=0
        total=0
        for u in self.userList:
            if not u["IsInfrastructure"] and u["IsActive"]:
                total+=1
                if "Администратор" not in u["Roles"] and "Редактор" not in u["Roles"]:
                    others+=1
                for key in self.usedLicenses:
                    if key in u["Roles"] : self.usedLicenses[key]+=1
        
        self.usedLicenses["Остальные пользователи"]=others
        self.usedLicenses["Всего"]=total
#--------------------создать пользователя и дать ему роль----------------------        
    def createUser(self, userName, userPassword, email, givenName, middleName, 
                   familyName, roles):
        
        payload = {
            "UserName": userName,
        }
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Authorization": self.userToken
        }
        ok, response = self.sendRequest("POST", '/admin/api/canUserBeCreated', headers, payload)
        if ok:
            headers["Content-type"]="application/json"
            payload = {
                        "Email":           email,
                        "FamilyName":      familyName,
                        "GivenName":       givenName,
                        "MiddleName":      middleName,
                        "Password":        userPassword,
                        "Roles":           roles,
                        "UserName":        userName,
                        "IsBlocked":       False,
                        "IsInfrastructure":False
                    }
            payload_put={"user":payload, "changePass":userPassword!=''}
            try:
                if response.json()['canUserBeCreated']:
                    ok, response = self.sendRequest("POST", '/admin/api/user',headers,dumps(payload))
                else:
                    ok, response = self.sendRequest("PUT", '/admin/api/user',headers, dumps(payload_put))
            except:
                pass

        return ok
            
#--------------------удалить пользователя----------------------        
    def removeUser(self, userName):
        payload = {
            "UserName": userName
        }
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": self.userToken
        }
        ok, response = self.sendRequest("DELETE", '/admin/api/user',  headers, payload)
        return ok
    
#-------------------------- load excel -------------------------
    def loadExcel(self, excel_filename, sheet_name):
        sheet_name='Sheet1'
        flag = True
        try:
            errorlog=''
            edata = read_excel(excel_filename, na_filter=False, sheet_name=sheet_name, header=0,
                       converters={'UserName':str,'Password':str,'UserName':str,'Email':str,'GivenName':str,'FamilyName':str,'MiddleName':str, 'Roles':str})
            edata.replace('nan', '')
            logins = edata['UserName'].tolist()
            passwords =  edata['Password'].tolist()
            emails =  edata['Email'].tolist()
            givennames= edata['GivenName'].tolist()
            familynames= edata['FamilyName'].tolist()
            middlenames= edata['MiddleName'].tolist()
            roles=edata['Roles'].tolist()
    
            for alogin,apass,aemail,agivenname,afamilyname,amiddlename,arole in zip(logins,passwords,emails,givennames, familynames, middlenames, roles):
                rolesList=arole.split(',')
                if alogin!='' and apass!='' and afamilyname!='':
                    if 'Все авторизованные пользователи' not in rolesList:
                        rolesList.append('Все авторизованные пользователи')
                    if  not self.createUser(alogin, apass, aemail, agivenname,amiddlename,afamilyname, rolesList):
                        errorlog+=alogin+" не создан по причине "+self.errorText+"\n"
                        flag = False
            if len(errorlog): self.errorText=errorlog
        except Exception as e:
            flag=False
            throwError(str(e))
        return flag
#-------------------------- save excel -------------------------
    def saveExcel(self, excel_filename, sheet_name):
        try:
            df = DataFrame.from_dict(self.userList)
            df = df.drop(df[df['IsBuiltIn']].index)
            df=df.drop(columns=['IsBuiltIn','IsInfrastructure','useLdap','IsActive', 'LockoutEndDate', 'AccessFailedCount', 'IsBlocked'])
            df.insert(1,'Password','')
            
            df.to_excel(excel_filename, sheet_name=sheet_name, index=False, engine='openpyxl')
        except Exception as e:
            throwError(str(e))

#--------------------создать пользователя и дать ему роль----------------------        
    def deactivateUser(self, userName):
        payload = {
            "UserName": userName,
        }
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Authorization": self.userToken
        }
        ok,response = self.sendRequest("POST", '/admin/api/deactivateUser',headers,payload)
        self.errorText=response.text
        return ok
#---------------------------------------------------------------------------        
    def sendRequest(self, req_type, rq_url, rq_headers, req_payload={}):
        self.hasError=False
        response=None
        try:
            response = requests.request(req_type, self.baseURL+rq_url,
                                        data=req_payload, headers=rq_headers, verify=False,
                                        timeout=self.timeout_value)
            if response.status_code!=200:
                raise Exception(str(response.status_code)+':'+response.text)
        except Exception as e:
            print(str(e))
            self.errorText=rq_url+':'+str(e)
            self.print_error(req_type, self.baseURL+rq_url, rq_headers, req_payload, self.errorText)
            self.hasError=True
        return not self.hasError,response
#---------------------------------------------------------------------------        
    def sendFile(self, rq_url,  req_data):
        self.hasError=False
        response=None
        try:
            headers = {
                "Content-Type": "application/octet-stream",
                "Authorization": "Bearer "+self.userToken,
                }

            response = requests.request('POST', self.baseURL+rq_url,
                                        data=req_data, headers=headers, verify=False,
                                        timeout=self.timeout_value)
            if response.status_code!=200:
                raise Exception(str(response.status_code)+':'+response.text)
        except Exception as e:
            self.errorText=rq_url+':'+str(e)
            print('File', self.baseURL+rq_url,headers, self.errorText)
            self.hasError=True
        return not self.hasError,response
#---------------------------------------------------------------------------        
    def sendJSON(self, req_type, rq_url, rq_headers, req_payload={}):
        self.hasError=False
        response=None
        try:

            response = requests.request(req_type, self.baseURL+rq_url,
                                        json=req_payload, headers=rq_headers, verify=False,
                                        timeout=self.timeout_value)
            if response.status_code!=200:
                raise Exception(str(response.status_code)+':'+response.text)
        except Exception as e:
            self.errorText=rq_url+':'+str(e)
            self.print_error(req_type, self.baseURL+rq_url, rq_headers, req_payload, self.errorText)
            self.hasError=True
        return not self.hasError,response
#----------------------------------------------------------------------------
    def getDashboards(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.userToken
        }
        self.dashboards = {}
        ok,response = self.sendRequest("GET",'/admin/api/dashboards', headers)
        if ok:
            try:
                for dashboard in response.json():
                    self.dashboards[dashboard['_id']]=dashboard['Name']
            except:
                pass
#--------------------get loki data----------------------        
    def getLokiDashboardRequests(self):
        if self.lokiApiKey=='':
            return
        step=int(2.5*self.since+1)
        end = int(time())
        start = end-self.since*3600
        querystring = {
            "direction":"BACKWARD",
            "limit":"1000",
            "query":"{component=\"dashboard-service\"} |=\"Произошел запрос на просмотр дашборда\"",
            "start": start*1000000000,
            "end": end*1000000000,
            "step":step
        }
        
        lokiheaders = {
            "Content-Type": "text/html",
            "Authorization": "Bearer "+self.lokiApiKey
            }
        self.dash_views={}
        
        self.hasError=False
        params = urlencode(querystring)
        ok,response = self.sendRequest('GET', '/grafana/api/datasources/proxy/1/loki/api/v1/query_range?'+params, lokiheaders)

        if not self.hasError:
            try:
                self.dash_views=response.json()
            except:
                pass
    
            self.saveIniFile({'LOKI':self.lokiApiKey})
#-----------------------------------------------------------------------------
    def print_error(self, req_type, rq_url, rq_headers, req_payload, errorText):
        global errorsCounter
        print(f'-----request error {errorsCounter} ----')
        print(errorText)
        print(f'-> at request {req_type} {rq_url}')
        print('-> HEADER',type(rq_headers))
        print(dumps(rq_headers, indent=2).encode('utf-8').decode('unicode_escape'))
        print('-> PAYLOAD',type(req_payload))
        print(dumps(req_payload, indent=2).encode('utf-8').decode('unicode_escape'))
        
        errorsCounter=errorsCounter+1
#------------------------------------------------------------------------------
    def saveIniFile(self, keyDict):
        with open('vitools.json','r') as f:
            try:
                urldata=load(f)
            except :
                urldata={}
        for i in keyDict:
            urldata[self.baseURL][i]=keyDict[i]
        with open('vitools.json', 'w', encoding='utf-8') as f:
            dump(urldata, f, ensure_ascii=False, indent=4) 