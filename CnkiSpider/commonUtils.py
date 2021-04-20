import os
from enum import Enum
import time
import requests
from CnkiSpider.proxy import ApeProxyManager
import logging
import scrapy
from CnkiSpider.file_util import FileUtil

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
    def getPatentCookies(cls, date, code, proxyDict=None):
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
        # logging.debug('requests获取cookis, 代理为%s' % str(proxyDict))
        if proxyDict:
            session_response = requests.get(search_url, params=params, proxies=cls.configReqestsProxyMeta(proxyDict))
        else:
            session_response = requests.get(search_url, params=params)
        cookies = requests.utils.dict_from_cookiejar(session_response.cookies)
        return cookies

    @classmethod
    def getPatentCookiesProxy(cls, date, code):
        '''
        根据日期，分类代码获取cookies,翻页时必须要有cookie,带代理
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
        # logging.debug('requests获取cookis, 代理为%s' % str(proxyDict))
        proxyDict = ApeProxyManager.getProxyDict()
        session_response = requests.get(search_url, params=params, proxies=cls.configReqestsProxyMeta(proxyDict))
        cookies = requests.utils.dict_from_cookiejar(session_response.cookies)
        return cookies

    @classmethod
    def configReqestsProxyMeta(cls, proxyDict):
        '''
        封装requests请求中的猿人云所必须的proxy参数
        :return:
        '''
        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyDict['ip'],
            "port": proxyDict['port'],
            "user": ApeProxyManager.id,
            "pass": ApeProxyManager.secret,
        }

        proxies = {
            "http": proxyMeta,
            "https": proxyMeta,
        }

    @classmethod
    def getPatentCookiesScrapy(cls, date, code):
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
        response = scrapy.Request(
            url=search_url,
            dont_filter=True,
            meta=params
        )
        headers = response.headers
        cookies = response.headers.getlist('Set-Cookie')
        print(cookies)
        return cookies

    @classmethod
    def getPaperAchCookiesProxy(cls, date, code):
        '''
        根据日期，分类代码获取论文和成果cookies,带代理
        :param cls:
        :param date:
        :param code:
        :return:
        '''
        search_url = 'https://kns.cnki.net/kns/request/SearchHandler.ashx/'
        now_time = time.strftime('%a %b %d %Y %H:%M:%S') + ' GMT+0800 (中国标准时间)'
        params = {
            "action": "",
            "NaviCode": code,
            "ua": "1.21",
            "isinEn": "1",
            "PageName": "ASP.brief_result_aspx",
            "DbPrefix": "SCDB",
            "DbCatalog": "中国学术文献网络出版总库",
            "ConfigFile": "SCDB.xml",
            "db_opt": "CJFQ,CJRF,CJFN,CDFD,CMFD,CPFD,IPFD,CCND,BDZK,CISD,SNAD,CCJD",
            "publishdate_from": date,
            "publishdate_to": date,
            "CKB_extension": "ZYW",
            "his": "0",
            '__': now_time
        }
        proxyDict = ApeProxyManager.getProxyDict()
        session_response = requests.get(search_url, params=params, proxies=cls.configReqestsProxyMeta(proxyDict))
        cookies = requests.utils.dict_from_cookiejar(session_response.cookies)
        return cookies

class ErrorUtil():
    '''
    错误判断工具类
    '''

    @classmethod
    def isBadResponse(cls, response):
        '''
        中间件如果接受到错误请求会构造一个url为空的response，这里判断是不是请求出错
        :param response:
        :return:
        '''
        if not response.url:  # 接收到url==''时
            return True
        else:
            return False

    @classmethod
    def markLinkError(cls, url, type):
        with open(FileUtil.errorLinkDir + type + 'Error.txt', 'a', encoding='utf-8') as file:
            file.write(url + '\n')

    @classmethod
    def markSecondError(cls, code, date, pagenum):
        if pagenum == 0:
            with open('error/erday.txt', 'a', encoding='utf-8') as f:
                f.write(code + '&' + date + '\n')
        else:
            with open('error/erpage.txt', 'a', encoding='utf-8') as f:
                f.write(code + '&' + date + '&' + str(pagenum) + '\n')

    @classmethod
    def markFirstError(cls, code, date, pagenum):
        if pagenum == 0:
            with open('error/errorday_' + date + '.txt', 'a', encoding='utf-8') as f:
                f.write(code + '&' + date + '\n')
        else:
            with open('error/errorpage_' + date + 'txt', 'a', encoding='utf-8') as f:
                f.write(code + '&' + date + '&' + str(pagenum) + '\n')

    @classmethod
    def easyErrorRecoder(cls, url):
        with open('error/EasyErrorRecorder.txt', 'a', encoding='utf-8') as file:
            file.write(url + '\n')

    @classmethod
    def markDayError(cls, type, code, date):
        with open(FileUtil.errorDayDir + type + '.txt', 'a', encoding='utf-8') as f:
            f.write(code + '&' + date + '\n')

    @classmethod
    def markPageError(cls, type, code, date, pagenum):
        with open(FileUtil.errorPageDir + type + '.txt', 'a', encoding='utf-8') as f:
            f.write(code + '&' + date + '&' + str(pagenum) + '\n')

if __name__ == '__main__':
    CookieUtil.getPatentCookiesScrapy(date='2020-01-01', code='A')
