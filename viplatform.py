# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 09:07:42 2023

@author: dcask
"""
import requests
from urllib.parse import urlencode
# import constants
from time import time
from json import load,dump, dumps
from pandas import DataFrame, read_excel
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

global errorsCounter
errorsCounter=0

def init(username,password, baseUrl) -> bool:
    global visiology
    visiology=ViPlatform()
    return visiology.init(username,password, baseUrl)
    
    
class ViPlatform():
    def getError(self)-> bool:
        if self.hasError:
            self.hasError=False
            return self.errorText
        return None
#-------------------- startup init ----------------------------
    def __init__(self):
        self.baseURL=''
        self. password=''
        self.lokiApiKey=''
        self.user=''
        self.timeout_value=10
        self.clearData()
#------------clear data-----------------------------
    def clearData(self):  
        self.since=24
        self.userToken=''
        self.db_roles=[]
        self.apiVersion=''
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
        with open('vitools.json','r') as f:
            try:
                urldata=load(f)
            except :
                urldata={}
        if self.baseURL in urldata:
            self.lokiApiKey=urldata[self.baseURL]['LOKI']
        return self.getToken()
    def show(self) -> None:
        print(self.user)
#-------------------- get access Token ----------------------------
    def getToken(self) -> bool:
        payload = {'grant_type':'password',
                   'scope':'openid profile email roles viqube_api viqubeadmin_api core_logic_facade \
                       dashboards_export_service script_service migration_service_api data_collection',
                   'response_type':'id_token+token',
                   'username': self.user,
                   'password':self.password
        }
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "authorization": "Basic cHVibGljX3JvX2NsaWVudDpAOVkjbmckXXU+SF4zajY="
        }

        ok,response = self.sendRequest('GET','/viqube/version', headers)
        if ok:
            self.apiVersion=response.json()['apiPartial']
        ok,response = self.sendRequest('POST','/idsrv/connect/token',headers,payload)
        if ok:
            self.userToken = response.json()['access_token']
            self.headers = {
                "Content-Type": "application/json",
                "X-API-VERSION": self.apiVersion,
                "Authorization": "Bearer "+self.userToken
            }
        return self.userToken!='' and self.apiVersion!=''
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
            
            roles = response.json()
            for role in roles:
                if not role['IsBuiltIn']:
                    roleList.append(role['Name'])
  
        roleList.append('Публичный доступ')
        roleList.append('Все авторизованные пользователи')
        return roleList
#------------------- set Roles ----------------
    def setRole(self, roleName, dbList)-> bool:
        payload = {
            "role": roleName,
            "databases": dbList
        }
        ok, response=self.sendRequest("PUT", '/viqube/accessrights/roledb', self.headers, payload)
        self.getDatabases()
        return ok
# ----------------------------- get databases ---------------
    def getDatabases(self) -> list:
        databases = []
        ok, response = self.sendRequest('GET','/viqube/databases',self.headers)
        if ok:
            dbs = response.json()
            for db in dbs:
                databases.append(db['name'])
        ok, response = self.sendRequest('GET','/viqube/accessrights/roledb',self.headers)
        if ok:
            self.db_roles = response.json()
        return databases
#------------------------- get license -------------------------
    def getLicense(self):
        # try:
        #     response = requests.get(self.baseURL+"/admin/license/limits", headers=self.headers, verify=constants.VI_SERTIFICATE_VERIFY)
        #     if response.status_code!=200:
        #         raise Exception(response.)
        #     else:
        #         self.license=response.json()
        # except Exception as e:
        #     self.errorText=str(e)
        #     print(self.errorText)
        #     self.hasError=True
        ok, response = self.sendRequest('GET',"/admin/license/limits", self.headers)
        if ok:
            self.license=response.json()
            
#------------------------- get users -------------------------
    def getUsers(self):
        # payload={"draw=5&columns%5B0%5D%5Bdata%5D=&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=false&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=false&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=FamilyName&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=GivenName&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=MiddleName&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=UserName&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=Email&columns%5B6%5D%5Bname%5D=&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B7%5D%5Bdata%5D=&columns%5B7%5D%5Bname%5D=&columns%5B7%5D%5Bsearchable%5D=true&columns%5B7%5D%5Borderable%5D=false&columns%5B7%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B7%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B8%5D%5Bdata%5D=&columns%5B8%5D%5Bname%5D=&columns%5B8%5D%5Bsearchable%5D=true&columns%5B8%5D%5Borderable%5D=false&columns%5B8%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B8%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=2&order%5B0%5D%5Bdir%5D=asc&start=0&length=10000&search%5Bvalue%5D=&search%5Bregex%5D=false&selectedRole=%D0%92%D1%81%D0%B5+%D0%B0%D0%B2%D1%82%D0%BE%D1%80%D0%B8%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%BD%D1%8B%D0%B5+%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D0%B8"
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
            self.userList=response.json()["data"]
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
        # print(self.usedLicenses)
#--------------------создать пользователя и дать ему роль----------------------        
    def createUser(self, userName, userPassword, email, givenName, middleName, 
                   familyName, roles):
        payload = {
            "UserName": userName,
        }
       
        ok, response = self.sendRequest("POST", '/admin/api/canUserBeCreated', self.headers, payload)
        if ok:
                    
            payload = {
                        'Email':email,
                        'FamilyName':familyName,
                        'GivenName':givenName,
                        'MiddleName':middleName,
                        'Password':userPassword,
                        'Roles':roles,
                        'UserName':userName
                    }
            payload_put={"changePass":False,"user":payload}
            if response.json()['canUserBeCreated']:
                ok, response = self.sendRequest("POST", '/admin/api/user',self.headers,payload)
            else:
                ok, response = self.sendRequest("PUT", '/admin/api/user',self.headers, payload_put)
        # print(payload_put)       

        return ok
            
#--------------------удалить пользователя----------------------        
    def removeUser(self, userName):
        payload = {
            "UserName": userName,
        }
        headers = {
            "Content-Type": "application/json",
            # "X-API-VERSION": self.apiVersion,
            "Authorization": self.userToken
        }
        # print(payload,headers)
        ok, response = self.sendRequest("DELETE", '/admin/api/user',  headers, payload)
        # print(response.text)
        return ok
    
#-------------------------- load excel -------------------------
    def loadExcel(self, excel_filename, sheet_name):
        sheet_name='Sheet1'
        flag = True
        errorlog=''
        # try:
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
                print(alogin, apass, aemail, agivenname,amiddlename,afamilyname, rolesList)
                if  not self.createUser(alogin, apass, aemail, agivenname,amiddlename,afamilyname, rolesList):
                    errorlog+=alogin+" не создан по причине "+self.errorText+"\n"
                    flag = False
        # except Exception as e:
        #     self.errorText=str(e)
        #     print(self.errorText)
        #     self.hasError=True
        if len(errorlog): self.errorText=errorlog
        return flag
#-------------------------- save excel -------------------------
    def saveExcel(self, excel_filename, sheet_name):
        df = DataFrame.from_dict(self.userList)
        df = df.drop(df[df['IsBuiltIn']].index)
        df=df.drop(columns=['IsBuiltIn','IsInfrastructure','useLdap','IsActive', 'LockoutEndDate', 'AccessFailedCount', 'IsBlocked', 'LastLogin', 'Created'])
        df.insert(1,'Password','')
        
        df.to_excel(excel_filename, sheet_name=sheet_name, index=False, engine='openpyxl')

#--------------------создать пользователя и дать ему роль----------------------        
    def deactivateUser(self, userName):
        payload = {
            "UserName": userName,
        }
        headers = {
            "Content-Type": "application/json",
            "X-API-VERSION": self.apiVersion,
            "Authorization": self.userToken
        }
        ok,response = self.sendRequest("POST", '/admin/api/deactivateUser',headers,payload)
        self.errorText=response.text
        return ok
#--------------------создать пользователя и дать ему роль----------------------        
    def sendRequest(self, req_type, rq_url, rq_headers, req_payload={}):
        self.hasError=False
        response=None
        try:

            response = requests.request(req_type, self.baseURL+rq_url,
                                        data=req_payload, headers=rq_headers, verify=False,
                                        timeout=self.timeout_value)
            response.encoding = 'utf-8'
            if response.status_code!=200:
                raise Exception(response.text)
        except Exception as e:
            self.errorText=rq_url+':'+str(e)
            self.print_error(req_type, self.baseURL+rq_url, rq_headers, req_payload, self.errorText)
            self.hasError=True
            # raise e
        return not self.hasError,response
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
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.userToken
        }
        lokiheaders = {
            "Content-Type": "text/html",
            "Authorization": "Bearer "+self.lokiApiKey
            }
        self.dash_views={}
        self.dashboards = {}
        self.hasError=False
        # response=None
        params = urlencode(querystring)
        # try:
        ok,response = self.sendRequest("GET",'/admin/api/dashboards', headers)
        if ok:
            for dashboard in response.json():
                self.dashboards[dashboard['_id']]=dashboard['Name']
            # else:
            #     raise Exception(response.text)

            # response = requests.get(self.baseURL+'/grafana/api/datasources/proxy/1/loki/api/v1/query_range', headers=lokiheaders, params=querystring,verify=False)
            ok,response = self.sendRequest('GET', '/grafana/api/datasources/proxy/1/loki/api/v1/query_range?'+params, lokiheaders)
        #     if not response.ok:
        #         raise Exception(response.text)
        # except Exception as e:
        #     self.errorText='Get loki:'+str(e)
        #     self.hasError=True
        #     # raise e
        if not self.hasError:
            
            self.dash_views=response.json()
            # print(self.dash_views,self.dashboards)
            #save to config file
            with open('vitools.json','r') as f:
                try:
                    urldata=load(f)
                except :
                    urldata={}
            urldata[self.baseURL]['LOKI']=self.lokiApiKey
            with open('vitools.json', 'w', encoding='utf-8') as f:
                dump(urldata, f, ensure_ascii=False, indent=4)       
    def print_error(self, req_type, rq_url, rq_headers, req_payload, errorText):
        global errorsCounter
        print(f'-----request error {errorsCounter} ----')
        print(errorText)
        print(f'-> at request {req_type} {rq_url}')
        print('-> HEADER')
        print(dumps(rq_headers, indent=2))
        print('-> PAYLOAD')
        print(dumps(req_payload, indent=2))
        
        errorsCounter=errorsCounter+1
