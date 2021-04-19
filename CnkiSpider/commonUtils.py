import os
from enum import Enum
import time
import requests

class StringUtil:

    @classmethod
    def stringHanlde(cls, s):
        '''
        将非空字符串去首尾空格，空类型设为""
        :param s:
        :return:
        '''
        if s and s is not None:
            s = s.strip()
        else:
            s = ""
        return s

class SpiderTypeEnum(Enum):
    '''
    爬虫类型枚举类，用于状态管理
    '''
    PATENT = "patent"
    JOURNAL = "journal"
    BOSHUO = "boshuo"
    ACHIEVEMENT = "achievement"
    PAPER_AND_ACH = "paperAch"

class CookieUtil():
    @classmethod

    def getPatentCookies(cls, date, code, proxy=None):
        '''
        根据日期，分类代码获取cookies,翻页时必须要有cookie
        :param date:
        :param code:
        :param proxy:
        :return:
        '''
        search_url = 'http://kns.cnki.net/kns/request/SearchHandler.ashx'
        times = time.strftime('%a %b %d %Y %H:%M:%S') + ' GMT+0800 (中国标准时间)'
        params = {
            "action": "",
            "NaviCode": code,
            "ua": "1.21",
            "isinEn": "0",
            "PageName": "ASP.brief_result_aspx",
            "DbPrefix": "SCPD",
            "DbCatalog": "中国专利数据库",
            "ConfigFile": "SCPD.xml",
            "db_opt": "SCOD",
            "db_value": "中国专利数据库",
            "date_gkr_from": date,
            "date_gkr_to": date,
            "his": '0',
            '__': times
        }
        if proxy:
            session_response = requests.get(search_url, params=params, proxy=proxy)
        else:
            session_response = requests.get(search_url, params=params)
        cookies = requests.utils.dict_from_cookiejar(session_response.cookies)
        return cookies

if __name__ == '__main__':
    pass
