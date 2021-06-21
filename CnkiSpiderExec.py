from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

#打包需要的import
import urllib.robotparser
import scrapy.spiderloader
import scrapy.statscollectors
import scrapy.logformatter
import scrapy.dupefilters
import scrapy.squeues
import scrapy.extensions.spiderstate
import scrapy.extensions.corestats
import scrapy.extensions.telnet
import scrapy.extensions.logstats
import scrapy.extensions.memusage
import scrapy.extensions.memdebug
import scrapy.extensions.feedexport
import scrapy.extensions.closespider
import scrapy.extensions.debug
import scrapy.extensions.httpcache
import scrapy.extensions.statsmailer
import scrapy.extensions.throttle
import scrapy.core.scheduler
import scrapy.core.engine
import scrapy.core.scraper
import scrapy.core.spidermw
import scrapy.core.downloader
import scrapy.downloadermiddlewares.stats
import scrapy.downloadermiddlewares.httpcache
import scrapy.downloadermiddlewares.cookies
import scrapy.downloadermiddlewares.useragent
import scrapy.downloadermiddlewares.httpproxy
import scrapy.downloadermiddlewares.ajaxcrawl
# import scrapy.downloadermiddlewares.chunked
import scrapy.downloadermiddlewares.decompression
import scrapy.downloadermiddlewares.defaultheaders
import scrapy.downloadermiddlewares.downloadtimeout
import scrapy.downloadermiddlewares.httpauth
import scrapy.downloadermiddlewares.httpcompression
import scrapy.downloadermiddlewares.redirect
import scrapy.downloadermiddlewares.retry
import scrapy.downloadermiddlewares.robotstxt
import scrapy.spidermiddlewares.depth
import scrapy.spidermiddlewares.httperror
import scrapy.spidermiddlewares.offsite
import scrapy.spidermiddlewares.referer
import scrapy.spidermiddlewares.urllength
import scrapy.pipelines
import scrapy.core.downloader.handlers.http
import scrapy.core.downloader.contextfactory

import scrapy_redis.pipelines
import scrapy_redis.dupefilter
import scrapy_redis.spiders
import scrapy_redis.scheduler
import scrapy_redis.queue


from enum import Enum
import time
import requests
from CnkiSpider.proxy import ApeProxyManager
import logging
import scrapy
from CnkiSpider.file_util import FileUtil
from scrapy.utils.project import get_project_settings
import sys
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from scrapy.http import HtmlResponse
from twisted.web.client import ResponseFailed
from scrapy.core.downloader.handlers.http11 import TunnelError
from CnkiSpider.file_util import FileUtil
from CnkiSpider.commonUtils import SpiderTypeEnum, ErrorUtil
import twisted
import scrapy
import time
import math
import re
import requests
from CnkiSpider.items import PatentContentItem
from CnkiSpider.items import ErrorUrlItem
from CnkiSpider.commonUtils import StringUtil
from CnkiSpider.statusManager import StatusManager
from CnkiSpider.commonUtils import SpiderTypeEnum, CookieUtil, ErrorUtil
from CnkiSpider.file_util import FileUtil
from CnkiSpider.proxy import ApeProxyManager
from scrapy.http.cookies import CookieJar
from scrapy_redis.spiders import RedisSpider
import base64


from CnkiSpider.customDownloadMiddlewares import *
from CnkiSpider.file_util import *
from CnkiSpider.pipelines import *
from CnkiSpider.proxy import *
from CnkiSpider.statusManager import *
from CnkiSpider.settings import binjiang_settings, dev_settings, product_settings, settings, settings_distribute, settings_distribute142out
from CnkiSpider.spiders import *
from CnkiSpider.spiders import patent, paperAchSpider, __init__
from CnkiSpider.proxy import *
from CnkiSpider.pipelines import *

from configparser import ConfigParser

# 弹窗
from tkinter import messagebox
from tkinter import *
import psutil

def alreadyRun():
    if os.path.exists("pid.txt"):
        with open("pid.txt", "r") as f:
            spid = f.readline()
            pid = int(spid.strip())
            pids = psutil.pids()
            # 文件中保存的进程号真正在运行
            # 采用覆盖模式模式，
            if pid in pids:
                return True
        with open("pid.txt", "w") as f2:
            f2.write(str(os.getpid()))
            return False
    else:
        with open("pid.txt", "w") as f:
            f.write(str(os.getpid()))
        return False

def getProcessIdfromName(processname):
    pl = psutil.pids()
    for pid in pl:
        if psutil.Process(pid).name() == processname:
            return pid
    return -1

def ifProcessNameExist(processname):
    if getProcessIdfromName(processname) >=0:
        return True
    else:
        return False

cp = ConfigParser()
# 与exe同目录
cp.read('./config.cfg')
spiderType = cp.get('spider', 'type')

root = Tk()
root.withdraw()  # ****实现主窗口隐藏


if alreadyRun():
    messagebox.showinfo(title="提示", message="已有程序在后台启动，请不要重复运行")
    exit(1)
else:
    process = CrawlerProcess(get_project_settings())
    messagebox.showinfo(title="提示",message="程序已在后台启动，请不要使用加速球或将此程序加入至白名单中，此弹窗可关闭")
    if not FileUtil.IfFinishTask():
        if spiderType == 'patent':
            process.crawl('patent')
            process.start()
        elif spiderType == 'paperAch':
            process.crawl('paperAch')
            process.start()