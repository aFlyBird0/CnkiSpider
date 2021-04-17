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
    def getProxyOnceString(self):
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
                    ip = res['data'][0]["ip"]
                    port = res['data'][0]['port']
                    # print(ip, port)
                    return "http://" + str(ip) + ":" + str(port)
                elif res['code'] == 11010030:
                    # "当前IP已绑定到其它订单，请先解绑"
                    logging.debug("重新请求ip中，原因如下：当前IP已绑定到其它订单，请先解绑")
                    self.getProxyOnceString()
                else:
                    print('代理请求错误，错误代码：%d,错误信息：%s' % (res['code'], res['msg'] ))
                    return None
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
            return None


    def getProxyString(self):
        for i in range(9):
            proxy = self.getProxyOnceString()
            if proxy:
                logging.debug('获取的ip代理:%s' % proxy)
                return proxy
            time.sleep(1)
        logging.error("代理连续获取9次都失败，程序退出")
        sys.exit()

    def getProxyOnceTuple(self):
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
                    ip = res['data'][0]["ip"]
                    port = res['data'][0]['port']
                    # print(ip, port)
                    # return "http://" + str(ip) + ":" + str(port)
                    return (ip, port)
                elif res['code'] == 11010030:
                    # "当前IP已绑定到其它订单，请先解绑"
                    logging.debug("重新请求ip中，原因如下：当前IP已绑定到其它订单，请先解绑")
                    self.getProxyOnceTuple()
                else:
                    print('代理请求错误，错误代码：%d,错误信息：%s' % (res['code'], res['msg'] ))
                    return None
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
            return None


    def getProxyTuple(self):
        for i in range(9):
            proxy = self.getProxyOnceTuple()
            if proxy:
                logging.debug('获取的ip代理:%s' % proxy)
                return proxy
            time.sleep(1)
        logging.error("代理连续获取9次都失败，程序退出")
        sys.exit()


if __name__ == '__main__':
    pm = ProxyManager()
    proxy = pm.getProxyOnce()
    print(proxy)
