# Scrapy settings for CnkiSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os
import random
from configparser import ConfigParser

BOT_NAME = 'CnkiSpider'

SPIDER_MODULES = ['CnkiSpider.spiders']
NEWSPIDER_MODULE = 'CnkiSpider.spiders'

# PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'CnkiSpider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# 日志级别
# LOG_LEVEL = 'WARNING'
LOG_LEVEL = 'INFO'
# LOG_FILE = '/home/lhp/common.log'

RETRY_ENABLED = True
RETRY_TIMES = 3
DOWNLOAD_TIMEOUT = 5

# 控制学科分类读取文件
# True为./dataSrc/codeTest.txt
# 删去此配置或 False 为 ./dataSrc/code.txt
CODE_FILE_TEST_MODE = False

# 分发模式，开启此模式后，每次启动会重置当前爬虫状态（即重新链接获取，但链接解析不会重复）
DISTRUBUTE_MODE = True


cp = ConfigParser()
# 与exe同目录
print(os.getcwd())
cp.read('./config.cfg')
# spiderType = cp.get('spider', 'type')
DATABASE_VERSION = cp.get('database', 'no')

# SPIDER_TYPE = SpiderTypeEnum.PATENT.value
# SPIDER_TYPE = SpiderTypeEnum.PAPER_AND_ACH.value
# START_DATE = '2020-07-01'
# END_DATE = '2020-07-31'

####################### proxy begin ##########################
# 是否开启，不开启就用本机
PROXY_OPEN = False
# PROXY_ID = "2021041600266801515"
PROXY_ID = "2121042901240321356"
PROXY_SECRET = "Ibmt35hmHCMlE2fH"
# 一次请求的代理的数量，目前买的套餐最高支持5
PROXY_LIMIT = 5
PROXY_FORMAT = "json"
PROXY_AUTH_MODE = "basic"
# 每个代理重复利用的次数
PROXY_REUSE = 10

###################### proxy end ##########################


#######################  redis begin  ##############################

# 指定Redis的主机名和端口
# 敏感信息配置在环境变量中
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = 16379

#  设置密码
REDIS_PARAMS = {
    'password': os.environ.get("REDIS_PWD"), #远程连接的密码
    'db': int(DATABASE_VERSION)              # 切换数据库
}

# 调度器启用Redis存储Requests队列
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# 确保所有的爬虫实例使用Redis进行重复过滤
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# 将Requests队列持久化到Redis，可支持暂停或重启爬虫
SCHEDULER_PERSIST = True

# [浅谈深度优先和广度优先(scrapy-redis) - 风不再来 - 博客园](https://www.cnblogs.com/yunxintryyoubest/p/9955867.html)
# Requests的调度策略，默认优先级队列
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue' # 优先级队列
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.LifoQueue' # 深度优先
# SCHEDULER_QUEUE_CLASS='scrapy_redis.queue.FifoQueue'    # 广度优先

# 将爬取到的items保存到Redis 以便进行后续处理
# ITEM_PIPELINES = {
#     'scrapy_redis.pipelines.RedisPipeline': 300
# }

ITEM_PIPELINES = {
    # 'scrapy_redis.pipelines.RedisPipeline': 299,
    'CnkiSpider.pipelines.CnkispiderPipeline': 300,
}

########################  redis end  ##############################

######################### mysql begin ##########################
# 敏感信息配置在环境变量中
MYSQL_HOST = os.environ.get("MYSQL_HOST")
MYSQL_PORT = "3306"
MYSQL_USER = "root"
MYSQL_PASSWD = os.environ.get("MYSQL_PWD")
MYSQL_DATABASE = "ZhiWangSpider"

#表名，将本机和服务器跑的表分开
MYSQL_TABLE = "status" + str(DATABASE_VERSION)

#状态表名，记录了当前爬取的日期和代码
STATUS_TABLE = "status" + str(DATABASE_VERSION)
# 链接获取错误表（用来重新获取某日期与某学科分类对应下的所有链接）
ERROR_CODE_TABLE = "errorCode" + str(DATABASE_VERSION)
# 链接请求错误表（用来重新请求错误链接）
ERROR_LINK_TABLE = "errorLink" + str(DATABASE_VERSION)

######################### mysql end #############################


# 重试状态码，其中400，407，478是猿人云返回的错误码
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 400, 407, 478]

############################ 下载速度控制 begin   ############################

# 下载延时
# DOWNLOAD_DELAY = 3
# 随机将上面的下载延时乘0.5-1.5
# RANDOMIZE_DOWNLOAD_DELAY=True

# 自动限速,必开，插件会自动调整合适的下载延迟
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_TARGET_CONCURRENCY = 8
AUTOTHROTTLE_START_DELAY = 3

# 并发控制，默认16
CONCURRENT_REQUESTS_PER_DOMAIN = 4
#CONCURRENT_REQUESTS_PER_IP = 16


####################### 下载速度控制 end ########################

# 代理中间件的开启与否
proxyMiddleWarePrio = 110 if PROXY_OPEN else None

DOWNLOADER_MIDDLEWARES = {

    'CnkiSpider.customDownloadMiddlewares.CnkiSpiderHeaderMiddleware': 100,

    'CnkiSpider.customDownloadMiddlewares.CnkispiderSpiderProxyMiddleware': proxyMiddleWarePrio,  #代理中间件
    # 全局错误中间件，注意这里是改的response，而下载中间件的response的优先级是反的
    # 全局错误中间件和重试中间件(RetryAndGetFailedUrl)都是改写了process_response
    # 而全局错误肯定是在重试之后再处理的，所以全局错误中间件的优先级比重试高（response优先级相反）
    'CnkiSpider.customDownloadMiddlewares.ProcessAllExceptionMiddleware': 120,
    'CnkiSpider.customDownloadMiddlewares.RetryAndGetFailedUrl': 130,
    # 'CnkiSpider.middlewares.CnkispiderDownloaderMiddleware': 543,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware':None,  #禁用自带重试中间件
}

# 自定义cookie
COOKIES_ENABLED = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:


# Disable cookies (enabled by default)
# COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'CnkiSpider.middlewares.CnkispiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html


# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'CnkiSpider.pipelines.CnkispiderPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

DEFAULT_REQUEST_HEADERS = {
        # Referer和User-Agent在customDownloadMiddlewares.CnkiSpiderHeaderMiddleware设置
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "kns.cnki.net",
        "Origin": "https://kns.cnki.net",
        # "Referer": "https://kns.cnki.net/kns/brief/result.aspx?dbprefix=SCDB&crossDbcodes=CJFQ,CDFD,CMFD,CPFD,IPFD,CCND,CCJD",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        # "User-Agent": random.choice(USER_AGENTS)
    }
