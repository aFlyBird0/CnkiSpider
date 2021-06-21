import os
from enum import Enum
import time
import requests
from CnkiSpider.proxy import ApeProxyManager
import logging
import scrapy
from CnkiSpider.file_util import FileUtil
from scrapy.utils.project import get_project_settings
import sys

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
        (已弃用，见getPatentCookiesProxy）根据日期，分类代码获取cookies,翻页时必须要有cookie
        :param date:
        :param code:
        :param proxy:
        :return:
        '''
        search_url = 'http://kns.cnki.net/kns/request/SearchHandler.ashx'
        times = time.strftime('%a %b %d %Y %H:%M:%S') + ' GMT+0800 (中国标准时间)'
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "kns.cnki.net",
            "Origin": "https://kns.cnki.net",
            "Referer": "https://kns.cnki.net/kns/brief/result.aspx?dbprefix=SCPD",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
        }
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
            session_response = requests.get(search_url, params=params, headers=headers,proxies=cls.configReqestsProxyMeta(proxyDict))
        else:
            session_response = requests.get(search_url, headers=headers, params=params)
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
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "kns.cnki.net",
            "Origin": "https://kns.cnki.net",
            "Referer": "https://kns.cnki.net/kns/brief/result.aspx?dbprefix=SCPD",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
        }
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

        settings = get_project_settings()

        # logging.debug('requests获取cookis, 代理为%s' % str(proxyDict))
        session_response = None
        for i in range(30):
            try:
                if settings.get("PROXY_OPEN"):
                    proxyDict = ApeProxyManager.getProxy()
                    session_response = requests.get(search_url, params=params, headers=headers, proxies=cls.configReqestsProxyMeta(proxyDict))
                else:
                    session_response = requests.get(search_url, params=params, headers=headers)
                if session_response.status_code == 200:
                    break
                else:
                    logging.warning("cookie获取失败，第%d次重新获取中" % (i+1))
                    time.sleep(1)
            except requests.exceptions.RequestException as e:
                logging.error('cookie获取发生异常 %s' % str(e))
        if not session_response:
            logging.error("cookie获取失败，程序退出")
            sys.exit()
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
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "kns.cnki.net",
            "Origin": "https://kns.cnki.net",
            "Referer": "https://kns.cnki.net/kns/brief/result.aspx?dbprefix=SCDB&crossDbcodes=CJFQ,CDFD,CMFD,CPFD,IPFD,CCND,CCJD",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
        }
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
        settings = get_project_settings()

        # logging.debug('requests获取cookis, 代理为%s' % str(proxyDict))
        session_response = None
        for i in range(30):
            try:
                if settings.get("PROXY_OPEN"):
                    proxyDict = ApeProxyManager.getProxy()
                    session_response = requests.get(search_url, params=params,headers=headers,
                                                    proxies=cls.configReqestsProxyMeta(proxyDict))
                else:
                    session_response = requests.get(search_url, params=params, headers=headers)
                if session_response.status_code == 200:
                    break
                else:
                    logging.warning("cookie获取失败，第%d次重新获取中" % (i + 1))
                    time.sleep(1)
            except requests.exceptions.RequestException as e:
                logging.error('cookie获取发生异常 %s' % str(e))
        if not session_response:
            logging.error("cookie获取失败，程序退出")
            sys.exit()
        cookies = requests.utils.dict_from_cookiejar(session_response.cookies)
        return cookies

import pymysql


class ErrorUtil():
    '''
    错误判断工具类
    '''
    settings = get_project_settings()
    host = settings.get("MYSQL_HOST")
    port = int(settings.get("MYSQL_PORT"))
    user = settings.get("MYSQL_USER")
    passwd = settings.get("MYSQL_PASSWD")
    database = settings.get("MYSQL_DATABASE")
    # table = settings.get("STATUS_TABLE")
    errorCodeTable = settings.get("ERROR_CODE_TABLE")
    errorLinkTable = settings.get("ERROR_LINK_TABLE")

    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, database=database)

    @classmethod
    def reCon(cls):
        """ MySQLdb.OperationalError异常"""
        # self.con.close()
        while True:
            try:
                cls.conn.ping()
                return
            except pymysql.err.OperationalError:
                logging.warning("mysql连接失败开始重连")
                cls.conn.ping(True)
            time.sleep(3)


    @classmethod
    def isBadResponse(cls, response):
        '''
        中间件如果接受到错误请求会构造一个url为空的response，这里判断是不是请求出错
        :param response:
        :return:
        '''
        if (not response.url) or (response.url == 'exception'):  # 接收到url==''或'exception'时
            return True
        else:
            return False

    # @classmethod
    # def markLinkError(cls, url, type, code):
    #     with open(FileUtil.errorLinkDir + type + 'Error.txt', 'a', encoding='utf-8') as file:
    #         file.write(url + '\n')

    @classmethod
    def markLinkError(cls, url, type: SpiderTypeEnum, code, date):
        '''
        记录出错的链接
        :param url:
        :param type:
        :param code:
        :return:
        '''
        cls.reCon()
        cursor = cls.conn.cursor()
        sql = "INSERT INTO `%s` (`type`, `code`, `link`, `date`)VALUES('%s', '%s', '%s', '%s')" % (cls.errorLinkTable, type.value, code, url, date)
        cursor.execute(sql)
        cls.conn.commit()

    # @classmethod
    # def markDayError(cls, type, code, date):
    #     with open(FileUtil.errorDayDir + type + '.txt', 'a', encoding='utf-8') as f:
    #         f.write(code + '&' + date + '\n')

    @classmethod
    def markCodeError(cls, type, code, date):
        '''
        记录某天某学科链接获取失败情况
        :param type:
        :param code:
        :param date:
        :return:
        '''
        cls.reCon()
        cursor = cls.conn.cursor()
        sql = "INSERT IGNORE INTO `%s` (`type`, `code`, `date`)VALUES('%s', '%s', '%s')" % (
            cls.errorCodeTable, type.value, code, date)
        cursor.execute(sql)
        cls.conn.commit()

    @classmethod
    def getOneErrorCode(cls, type:SpiderTypeEnum = None):
        if type:
            sql = "select `id`, `type`, `code`, `date` from `%s` where `type` = '%s' limit 1" % (cls.errorCodeTable, type.value)
        else:
            sql = "select `id`, `type`, `code`, `date` from `%s` limit 1" % (cls.errorCodeTable)
        cls.reCon()
        cursor = cls.conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        if not result:
            return None
        else:
            return result

    @classmethod
    def getOneErrorLink(cls, type: SpiderTypeEnum = None):
        if type:
            sql = "select `id`, `type`, `code`, `link`, `date` from `%s` where `type` = '%s' limit 1" % (
            cls.errorLinkTable, type.value)
        else:
            sql = "select `id`, `type`, `code`, `link`, `date` from `%s` limit 1" % (cls.errorLinkTable)
        cls.reCon()
        cursor = cls.conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        if not result:
            return None
        else:
            return result

    @classmethod
    def deleteErrorCode(cls, id:int):
        sql = "delete from `%s` where `id` = %d" % (cls.errorCodeTable, id)
        cls.reCon()
        cursor = cls.conn.cursor()
        cursor.execute(sql)
        cls.conn.commit()

    @classmethod
    def deleteErrorLink(cls, id: int):
        sql = "delete from `%s` where `id` = %d" % (cls.errorLinkTable, id)
        cls.reCon()
        cursor = cls.conn.cursor()
        cursor.execute(sql)
        cls.conn.commit()

    @classmethod
    def closeConn(cls):
        '''
        关闭数据库连接
        :return:
        '''
        cls.conn.close()


if __name__ == '__main__':
    CookieUtil.getPatentCookiesScrapy(date='2020-01-01', code='A')
