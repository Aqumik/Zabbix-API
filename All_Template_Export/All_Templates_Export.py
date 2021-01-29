# -*- coding:UTF-8 -*-
# @aqumik 2021-1-29 Python3 导出Zabbix所有模板，虽然xml格式有点难看，但是直接导入到服务器就可使用！！
# 具体参数可以查看注释，SSL直接使用了False
import json
import requests

class Zabbix(object):
    def __init__(self,url,header,user,password):
        self.url = url
        self.header = header
        self.id = 0
        self.user = user
        self.password = password

    # def get_auth(self):
    #     req = json.dumps(
    #         {
    #             "jsonrpc": "2.0",
    #             "method": "user.login",
    #             "params": {
    #                 "user": "Admin",
    #                 "password": "zabbix"
    #             },
    #             "id": 0
    #         }
    #     )
    #     ret = requests.post(url=self.url, data=req, headers=self.header).json()
    #     ret = ret['result']
    #     authid = ret
    #     print(authid)

    # 验证模块，提交的json验证都在此处
    def json_obj(self,method,auth=True,params={}):
        obj = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
                'auth':auth,
                "id":self.id
            }
        # 需要删除后才能json格式化请求，否则无法删除 auth
        if not auth:
            del  obj["auth"]
        obj = json.dumps(obj)
        return obj

    # 登陆模块
    def user_login(self):
        data = self.json_obj(method="user.login",auth=False,params={"user":self.user,"password":self.password})
        req = requests.post(url=self.url,headers=self.header,data=data,verify=False)
        req = req.json()['result']
        return req

    # 退出模块
    def user_logout(self,auth):
        # auth = self.user_login()

        print('********退出模块，认证id',auth)
        data = self.json_obj(method="user.logout",auth=auth,params={})
        req = requests.post(url=self.url,headers=self.header,data=data,verify=False)
        if req.json()['result'] == True:
            print('退出成功')
        else:
            print('退出失败')
        return req.text

    # 获取所有模板id
    def all_template_get(self,auth=True):
        print('all_template_get获取到认证id',auth)
        data = self.json_obj(method="template.get",auth=auth,
                             params={
                                 "output": [
                                     "host",
                                     "templateid"
                                 ]
                             })
        req = requests.post(url=self.url,headers=self.header,data=data,verify=False)
        print(req.json()['result'])
        # self.user_logout(auth=auth)
        #返回值是所有模板名字+id的数组
        return req.json()['result']

    #导出所有模板
    def all_template_xml(self,auth):
        # auth = self.user_login()
        all_template_get = self.all_template_get(auth=auth)
        for tempalte in all_template_get:
            template_name = tempalte['host']
            template_id = str(tempalte['templateid'])
            print('*********模板名字：%s, id：%s' % (template_name, template_id))
            data = self.json_obj(method="configuration.export",auth=auth,
                                 params={
                                     "options":{
                                         "templates": [
                                             template_id
                                         ]
                                     },
                                     "format": "xml"
                                 })
            req = requests.post(url=self.url,headers=self.header,data=data,verify=False).json()
            req = req['result']
            #将得到的xml文件输出
            myxml = open(template_name+'.xml',mode='a',encoding='utf-8')
            print(req,file=myxml)
            myxml.close()
            print(req)
        print('****************all_template_xml获取到的auth',auth)



if __name__ == '__main__':

    url = 'http://192.168.20.180/zabbix/api_jsonrpc.php'
    header = {'Content-Type': 'application/json'}
    user = 'Admin'
    password = 'zabbix'
    authid = Zabbix(url,header,user,password).user_login()
    print(authid)
    Zabbix(url, header,user,password).all_template_xml(authid)
    Zabbix(url, header,user,password).user_logout(authid)
