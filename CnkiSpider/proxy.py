import hashlib
import requests
import json
from scrapy.utils.project import get_project_settings
import logging
import sys
import time
import base64
import random

class ApeProxyManager:
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

    # 目前剩余的ip
    proxyLeft = 0
    # ip列表
    proxies = []
    # ip复用的最大次数
    reuseMAX = settings.get("PROXY_REUSE")
    # ip已经复用的次数
    reuseCur = 0

    @classmethod
    def getProxiesDicts(cls):
        '''
        一次性获取多个代理
        :return:
        '''
        try:
            response = requests.get(
                url="http://tunnel-api.apeyun.com/q",
                params=ApeProxyManager.params,
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
                    # print(data)
                    cls.proxies = []
                    for d in data:
                        cls.proxies.append({'ip': d['ip'], 'port':str(d['port'])})
                    logging.debug('获取到的所有代理:%s', str(cls.proxies))
                    # print(cls.proxies)
                    return True
                elif res['code'] == 11010030:
                    # "当前IP已绑定到其它订单，请先解绑"
                    logging.debug("重新请求ip中，原因如下：当前IP已绑定到其它订单，请先解绑")
                    time.sleep(1)
                    cls.getProxiesDicts()
                else:
                    logging.debug('代理请求错误，错误代码：%d,错误信息：%s' % (res['code'], res['msg'] ))
                    return False
        except requests.exceptions.RequestException:
            logging.error('代理获取时，HTTP Request failed')
            return False

    @classmethod
    def getProxyDict(cls):
        if cls.proxyLeft > 0:
            # proxy = cls.proxies[ApeProxyManager.limit-cls.proxyLeft]
            proxy = random.choice(cls.proxies)
            logging.debug("代理复用，获取到的代理：%s:%s" % (proxy['ip'], proxy['port']))
            cls.proxyLeft -= 1
            # logging.debug("当前剩余代理数量：%s" % cls.proxyLeft)
            return proxy
        else:
            for i in range(12):
                if cls.getProxiesDicts():
                    # 总可用数量等于代理数量 * 最大复用次数
                    cls.proxyLeft = ApeProxyManager.limit * ApeProxyManager.reuseMAX
                    # proxy = cls.proxies[ApeProxyManager.limit-cls.proxyLeft]
                    proxy = random.choice(cls.proxies)
                    cls.proxyLeft -= 1
                    logging.debug("请求新批次代理，获取到的代理：%s:%s" % (proxy['ip'], proxy['port']))
                    # logging.debug("当前剩余代理数量：%s" % cls.proxyLeft)
                    return proxy
                time.sleep(1)
            logging.error("连续十二次获取ip失败，程序退出")
            sys.exit()

    @classmethod
    def getProxyString(cls):
        if cls.proxyLeft > 0:
            # proxy = cls.proxies[ApeProxyManager.limit-cls.proxyLeft]
            proxy = random.choice(cls.proxies)
            logging.debug("代理复用，获取到的代理：%s:%s" % (proxy['ip'], proxy['port']))
            cls.proxyLeft -= 1
            # logging.debug("当前剩余代理数量：%s" % cls.proxyLeft)
            return ("http://" + proxy['ip'] + ":" + str(proxy['port']))
        else:
            for i in range(24):
                if cls.getProxiesDicts():
                    cls.proxyLeft = ApeProxyManager.limit * ApeProxyManager.reuseMAX
                    # proxy = cls.proxies[ApeProxyManager.limit-cls.proxyLeft]
                    proxy = random.choice(cls.proxies)
                    cls.proxyLeft -= 1
                    logging.debug("请求新批次代理，获取到的代理：%s:%s" % (proxy['ip'], proxy['port']))
                    # logging.debug("当前剩余代理数量：%s" % cls.proxyLeft)
                    return  ("http://" + proxy['ip'] + ":" + str(proxy['port']))
                # 代理一般是几秒才能请求一次，所以可能存在请求过快导致报错的情况，这时候暂停一秒再次请求
                time.sleep(1)
            logging.error("连续24次获取ip失败，程序退出")
            sys.exit()

    @classmethod
    def proxyDict2String(cls, proxy):
        '''
        将字典形式的代理转化为http://ip:port形式
        :param proxy:
        :return:
        '''
        if not proxy:
            return proxy
        return "http://" + proxy['ip'] + ":" + str(proxy['port'])

if __name__ == '__main__':
    for i in range(1000):
        proxy = ApeProxyManager.getProxyDict()
        # print(proxy)
