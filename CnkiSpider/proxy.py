import hashlib
import requests
import json
from scrapy.utils.project import get_project_settings
import logging
import sys
import time
import base64

class ProxyManager:
    settings = get_project_settings()
    open = settings.get("PROXY_OPEN")
    id = settings.get("PROXY_ID")
    secret = settings.get("PROXY_SECRET")
    limit = settings.get("PROXY_LIMIT")
    format = settings.get("PROXY_FORMAT")
    auth_mode = settings.get("PROXY_AUTH_MODE")
    proxyUser = id
    proxyPass = secret
    proxyAuth = "Basic " + base64.urlsafe_b64encode(bytes((proxyUser + ":" + proxyPass), "ascii")).decode("utf8")
    params = {
        "id": id,
        "secret": secret,
        "limit": limit,
        "format": format,
        "auth_mode": auth_mode
    }

    def __init__(self):
        # 目前剩余的ip
        self.proxyLeft = 0
        self.proxies = []

    def getProxiesDicts(self):
        '''
        一次性获取多个代理
        :return:
        '''
        try:
            response = requests.get(
                url="http://tunnel-api.apeyun.com/q",
                params=ProxyManager.params,
                headers={
                    "Content-Type": "text/plain; charset=utf-8",
                }
            )
            # print('Response HTTP Status Code: {status_code}'.format(
            #     status_code=response.status_code))
            if response.status_code == 200:
                # print(response.text)
                res = json.loads(response.text)
                if res['code'] == 200:
                    # return (res['data'][0]["ip"], res['data'][0]['port'])
                    # print(res)
                    data = res['data']
                    for d in data:
                        self.proxies.append({'ip': d['ip'], 'port':d['port']})
                    print('获取到的所有代理', self.proxies)
                    return True
                elif res['code'] == 11010030:
                    # "当前IP已绑定到其它订单，请先解绑"
                    logging.debug("重新请求ip中，原因如下：当前IP已绑定到其它订单，请先解绑")
                    time.sleep(1)
                    self.getProxiesDicts()
                else:
                    print('代理请求错误，错误代码：%d,错误信息：%s' % (res['code'], res['msg'] ))
                    return False
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
            return False

    def getProxyTuple(self):
        if self.proxyLeft > 0:
            proxy = self.proxies[ProxyManager.limit-self.proxyLeft]
            logging.debug("获取到的代理：%s:%d" % (proxy['ip'], proxy['port']))
            return (proxy['ip'], proxy['port'])
        else:
            for i in range(12):
                if self.getProxiesDicts():
                    self.proxyLeft = ProxyManager.limit
                    proxy = self.proxies[ProxyManager.limit-self.proxyLeft]
                    self.proxyLeft -= 1
                    logging.debug("获取到的代理：%s:%d" % (proxy['ip'], proxy['port']))
                    return  (proxy['ip'], proxy['port'])
                time.sleep(1)
            logging.error("连续十二次获取ip失败，程序退出")
            sys.exit()

    def getProxyString(self):
        if self.proxyLeft > 0:
            proxy = self.proxies[ProxyManager.limit-self.proxyLeft]
            logging.debug("获取到的代理：%s:%d" % (proxy['ip'], proxy['port']))
            return ("http://" + proxy['ip'] + ":" + str(proxy['port']))
        else:
            for i in range(12):
                if self.getProxiesDicts():
                    self.proxyLeft = ProxyManager.limit
                    proxy = self.proxies[ProxyManager.limit-self.proxyLeft]
                    self.proxyLeft -= 1
                    logging.debug("获取到的代理：%s:%d" % (proxy['ip'], proxy['port']))
                    return  ("http://" + proxy['ip'] + ":" + str(proxy['port']))
                time.sleep(1)
            logging.error("连续十二次获取ip失败，程序退出")
            sys.exit()


    # def getProxyOnceString(self):
    #     '''
    #     旧版接口，一次性获取一个字符串形式的代理，请求执行部分
    #     :return:
    #     '''
    #     try:
    #         response = requests.get(
    #             url="http://tunnel-api.apeyun.com/q",
    #             params=ProxyManager.params,
    #             headers={
    #                 "Content-Type": "text/plain; charset=utf-8",
    #             }
    #         )
    #         # print('Response HTTP Status Code: {status_code}'.format(
    #         #     status_code=response.status_code))
    #         if response.status_code == 200:
    #             # print(response.text)
    #             res = json.loads(response.text)
    #             if res['code'] == 200:
    #                 # return (res['data'][0]["ip"], res['data'][0]['port'])
    #                 ip = res['data'][0]["ip"]
    #                 port = res['data'][0]['port']
    #                 # print(ip, port)
    #                 return "http://" + str(ip) + ":" + str(port)
    #             elif res['code'] == 11010030:
    #                 # "当前IP已绑定到其它订单，请先解绑"
    #                 logging.debug("重新请求ip中，原因如下：当前IP已绑定到其它订单，请先解绑")
    #                 time.sleep(1)
    #                 self.getProxyOnceString()
    #             else:
    #                 print('代理请求错误，错误代码：%d,错误信息：%s' % (res['code'], res['msg'] ))
    #                 return None
    #     except requests.exceptions.RequestException:
    #         print('HTTP Request failed')
    #         return None


    # def getProxyString(self):
    #     '''
    #     旧版接口，一次性获取一个字符串形式的代理，调用逻辑部分
    #     :return:
    #     '''
    #     for i in range(12):
    #         proxy = self.getProxyOnceString()
    #         if proxy:
    #             logging.debug('获取的ip代理:%s' % proxy)
    #             return proxy
    #         time.sleep(1)
    #     logging.error("代理连续获取12次都失败，程序退出")
    #     sys.exit()

    # def getProxyOnceTuple(self):
    #     try:
    #         response = requests.get(
    #             url="http://tunnel-api.apeyun.com/q",
    #             params=ProxyManager.params,
    #             headers={
    #                 "Content-Type": "text/plain; charset=utf-8",
    #             }
    #         )
    #         # print('Response HTTP Status Code: {status_code}'.format(
    #         #     status_code=response.status_code))
    #         if response.status_code == 200:
    #             # print(response.text)
    #             res = json.loads(response.text)
    #             if res['code'] == 200:
    #                 # return (res['data'][0]["ip"], res['data'][0]['port'])
    #                 ip = res['data'][0]["ip"]
    #                 port = res['data'][0]['port']
    #                 # print(ip, port)
    #                 # return "http://" + str(ip) + ":" + str(port)
    #                 return (ip, port)
    #             elif res['code'] == 11010030:
    #                 # "当前IP已绑定到其它订单，请先解绑"
    #                 logging.debug("重新请求ip中，原因如下：当前IP已绑定到其它订单，请先解绑")
    #                 self.getProxyOnceTuple()
    #             else:
    #                 print('代理请求错误，错误代码：%d,错误信息：%s' % (res['code'], res['msg'] ))
    #                 return None
    #     except requests.exceptions.RequestException:
    #         print('HTTP Request failed')
    #         return None


    # def getProxyTuple(self):
    #     for i in range(9):
    #         proxy = self.getProxyOnceTuple()
    #         if proxy:
    #             logging.debug('获取的ip代理:%s' % proxy)
    #             return proxy
    #         time.sleep(1)
    #     logging.error("代理连续获取9次都失败，程序退出")
    #     sys.exit()


if __name__ == '__main__':
    pm = ProxyManager()
    for i in range(10):
        proxy = pm.getProxyTuple()
        print(proxy)
