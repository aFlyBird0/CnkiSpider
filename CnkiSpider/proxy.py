import hashlib
import requests
import json
from scrapy.utils.project import get_project_settings
import logging
import sys
import time

class ProxyManager:
    settings = get_project_settings()
    open = settings.get("PROXY_OPEN")
    id = settings.get("PROXY_ID")
    secret = settings.get("PROXY_SECRET")
    limit = settings.get("PROXY_LIMIT")
    format = settings.get("PROXY_FORMAT")
    auth_mode = settings.get("PROXY_AUTH_MODE")
    params = {
        "id": id,
        "secret": secret,
        "limit": limit,
        "format": format,
        "auth_mode": auth_mode
    }
    def getProxyOnce(self):
        try:
            response = requests.get(
                url="http://tunnel-api.apeyun.com/q?id=2021041600266801515&secret=Ibmt35hmHCMlE2fH&limit=1&format=txt&auth_mode=basic",
                params=ProxyManager.params,
                headers={
                    "Content-Type": "text/plain; charset=utf-8",
                }
            )
            print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            if response.status_code == 200:
                res = json.loads(response.text)
                # return (res['data'][0]["ip"], res['data'][0]['port'])
                return "http://" + res['data'][0]["ip"] + ":" + res['data'][0]['port']
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
            return None

    def getProxy(self):
        for i in range(9):
            proxy = self.getProxyOnce()
            if proxy:
                return proxy
            time.sleep(1)
        logging.error("代理连续获取9次都失败，程序退出")
        sys.exit()
