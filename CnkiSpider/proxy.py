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
                        cls.proxies.append({'ip': d['ip'], 'port':d['port']})
                    logging.debug('获取到的所有代理:%s', str(cls.proxies))
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
    def getProxyTuple(cls):
        # 上次请求的代理还没用完
        if cls.proxyLeft > 0:
            proxy = {}
            # 当前代理还可被复用
            if cls.reuseCur < cls.reuseMAX:
                proxy = cls.proxies[ProxyManager.limit - cls.proxyLeft]
                logging.debug("代理复用，获取到的代理：%s:%d" % (proxy['ip'], proxy['port']))
                cls.reuseCur += 1
            # 当前代理达到最大复用次数，更换同一批次的下一个代理
            else:
                proxy = cls.proxies[ProxyManager.limit - cls.proxyLeft]
                logging.debug("当前代理已复用完，获取到的同一批次下一代理：%s:%d" % (proxy['ip'], proxy['port']))
                cls.reuseCur = 1
                cls.proxyLeft -= 1
            # logging.debug("当前剩余代理数量：%s" % cls.proxyLeft)
            return (proxy['ip'], proxy['port'])
        # 当前无可用代理，请求新代理
        else:
            for i in range(12):
                if cls.getProxiesDicts():
                    cls.proxyLeft = ProxyManager.limit
                    proxy = cls.proxies[ProxyManager.limit-cls.proxyLeft]
                    cls.proxyLeft -= 1
                    cls.reuseCur = 1
                    logging.debug("当前批次的所有代理都已用完，获取到的代理：%s:%d" % (proxy['ip'], proxy['port']))
                    # logging.debug("当前剩余代理数量：%s" % cls.proxyLeft)
                    return  (proxy['ip'], proxy['port'])
                time.sleep(1)
            logging.error("连续十二次获取ip失败，程序退出")
            sys.exit()

    @classmethod
    def getProxyString(cls):
        # 上次请求的代理还没用完
        if cls.proxyLeft > 0:
            proxy = {}
            # 当前代理还可被复用
            if cls.reuseCur < cls.reuseMAX:
                proxy = cls.proxies[ProxyManager.limit - cls.proxyLeft]
                logging.debug("代理复用，获取到的代理：%s:%d" % (proxy['ip'], proxy['port']))
                cls.reuseCur += 1
            # 当前代理达到最大复用次数，更换同一批次的下一个代理
            else:
                proxy = cls.proxies[ProxyManager.limit - cls.proxyLeft]
                logging.debug("当前代理已复用完，获取到的同一批次下一代理：%s:%d" % (proxy['ip'], proxy['port']))
                cls.reuseCur = 1
                cls.proxyLeft -= 1
            # logging.debug("当前剩余代理数量：%s" % cls.proxyLeft)
            return "http://" + proxy['ip'] + ":" + str(proxy['port'])
        # 当前无可用代理，请求新代理
        else:
            for i in range(12):
                if cls.getProxiesDicts():
                    cls.proxyLeft = ProxyManager.limit
                    proxy = cls.proxies[ProxyManager.limit-cls.proxyLeft]
                    cls.proxyLeft -= 1
                    cls.reuseCur = 1
                    logging.debug("当前批次的所有代理都已用完，获取到的代理：%s:%d" % (proxy['ip'], proxy['port']))
                    # logging.debug("当前剩余代理数量：%s" % cls.proxyLeft)
                    return  "http://" + proxy['ip'] + ":" + str(proxy['port'])
                time.sleep(1)
            logging.error("连续十二次获取ip失败，程序退出")
            sys.exit()

if __name__ == '__main__':
    for i in range(10):
        proxy = ProxyManager.getProxyTuple()
        print(proxy)
