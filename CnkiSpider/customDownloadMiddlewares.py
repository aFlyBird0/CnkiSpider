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
from scrapy.utils.project import get_project_settings



class ProcessAllExceptionMiddleware(object):
    ALL_EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
                      ConnectionRefusedError, ConnectionDone, ConnectError,
                      ConnectionLost, TCPTimedOutError, ResponseFailed,
                      IOError, TunnelError, twisted.internet.error.ConnectionLost)

    # def process_response(self, request, response, spider):
    #     # 捕获状态码为40x/50x的response
    #     if str(response.status).startswith('4') or str(response.status).startswith('5'):
    #         # 随意封装，直接返回response，spider代码中根据url==''来处理response
    #         response = HtmlResponse(url='')
    #         return response
    #     # 其他状态码不处理
    #     return response



    def process_exception(self, request, exception, spider):
        # 捕获RetryAndGetFailedUrl的重试中间件捕获后剩下的异常
        if not isinstance(exception, self.ALL_EXCEPTIONS):
            # 在日志中打印异常类型
            logging.error('全局异常捕获: %s' % (exception))
            # 随意封装一个response，返回给spider
            response = HtmlResponse(url='exception')
            return response

    def process_response(self, request, response, spider):
        if str(response.status).startswith('4') or str(response.status).startswith('5'):
            # # 随意封装，直接返回response，spider代码中根据url==''来处理response
            key = request.cb_kwargs
            # print(request)
            # print("截取到了错误请求")
            if spider.name == SpiderTypeEnum.PATENT.value:
                # print(key)
                if key['requestType'] in  ['PatentGetFirstPage', 'PatentGetLinks']:
                    # print('请求状态:%s' % response.status)
                    # print('请求链接:%s' % response.meta['url'])
                    # print('响应内容:%s' % response.text)
                    ErrorUtil.markCodeError(type=SpiderTypeEnum.PATENT, code=key['code'], date=key['date'])
                # elif key['requestType'] == 'PatentGetLinks':
                #     ErrorUtil.markPageError(type=SpiderTypeEnum.PATENT, code=key['code'], date=key['date'],
                #                        pagenum=key['pagenum'])
                elif key['requestType'] == "patentGetContent":
                    ErrorUtil.markLinkError(type=SpiderTypeEnum.PATENT, url=key['url'], code=key['code'], date=key['date'])
            elif spider.name == SpiderTypeEnum.PAPER_AND_ACH.value:
                if key['requestType'] in ["PaperAchGetFirstPage", 'PaperAchGetLinks']:
                    ErrorUtil.markCodeError(type=SpiderTypeEnum.PAPER_AND_ACH, code=key['code'], date=key['date'])
                # elif key['requestType'] == 'PaperAchGetLinks':
                #     ErrorUtil.markPageError(type=SpiderTypeEnum.PAPER_AND_ACH, code=key['code'], date=key['date'],
                #                             pagenum=key['pagenum'])
                elif key['requestType'] == "JournalGetContent":
                    ErrorUtil.markLinkError(type=SpiderTypeEnum.JOURNAL, url=key['url'], code=key['code'], date=key['date'])
                elif key['requestType'] == "BoshuoGetContent":
                    ErrorUtil.markLinkError(type=SpiderTypeEnum.BOSHUO, url=key['url'], code=key['code'], date=key['date'])
                elif key['requestType'] == "AchGetContent":
                    ErrorUtil.markLinkError(type=SpiderTypeEnum.ACHIEVEMENT, url=key['url'], code=key['code'], date=key['date'])
            # 返回一个出错的response，前端判断url为空就说明之前的请求有问题
            return HtmlResponse(url='')
        return response


    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)




from CnkiSpider.proxy import ApeProxyManager


class CnkispiderSpiderProxyMiddleware:
    '''
    给所有的request加上代理
    '''
    def process_request(self, request, spider):
        request.meta["proxy"] = ApeProxyManager.getProxy()['string']
        request.headers["Proxy-Authorization"] = ApeProxyManager.proxyAuth
        return None

import random

class CnkiSpiderHeaderMiddleware:

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
        "Mozilla/5.0 (Android; Mobile; rv:14.0) Gecko/14.0 Firefox/14.0",
        "Mozilla/5.0 (Android; Tablet; rv:14.0) Gecko/14.0 Firefox/14.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20130331 Firefox/21.0",
        "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0",
        "Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19",
        "Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19",
        "Mozilla/5.0 (Linux; Android 4.1.2; Nexus 7 Build/JZ054K) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
        "Mozilla/5.0 (compatible; WOW64; MSIE 10.0; Windows NT 6.2)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
        "Opera/9.80 (Windows NT 6.1; WOW64; U; en) Presto/2.10.229 Version/11.62"]

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', random.choice(self.USER_AGENTS))
        # 专利和论文设置不同的Refer
        if spider.name == SpiderTypeEnum.PAPER_AND_ACH:
            request.headers.setdefault("Referer", "https://kns.cnki.net/kns/brief/result.aspx?dbprefix=SCDB&crossDbcodes=CJFQ,CDFD,CMFD,CPFD,IPFD,CCND,CCJD")
        elif spider.name == SpiderTypeEnum.PATENT:
            request.headers.setdefault("Referer", "https://kns.cnki.net/kns/brief/result.aspx?dbprefix=SCOD")




import time
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
import logging
from CnkiSpider.commonUtils import ApeProxyManager


class RetryAndGetFailedUrl(RetryMiddleware):
    start_date = time.strftime('%Y-%m-%d', time.localtime())
    def process_response(self, request, response, spider):
        # 在之前构造的request中可以加入meta信息dont_retry来决定是否重试
        if request.meta.get('dont_retry', False):
            return response

        # 检查状态码是否在列表中，在的话就调用_retry方法进行重试
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            # 在此处进行自己的操作，如删除不可用代理，打日志等
            settings = get_project_settings()
            if settings.get("PROXY_OPEN"):
                oldProxyString = request.meta["proxy"]
                ApeProxyManager.removeBadProxy(oldProxyString)
                proxyString = ApeProxyManager.getProxy()['string']
                request.meta["proxy"] = proxyString
                logging.warning('切换代理(%s)重试中(%s)' % (proxyString, request.url))
            else:
                logging.warning('未启用代理，重试中(%s)' % (request.url))
            self.save_url(request, spider)
            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        if (
            isinstance(exception, self.EXCEPTIONS_TO_RETRY)
            and not request.meta.get('dont_retry', False)
        ):
            # logging.warning('错误异常捕捉:%s,开始重试' % exception)
            logging.warning("捕获到异常 %s" % exception)
            settings = get_project_settings()
            retries = request.meta.get('retry_times', 0) + 1
            if settings.get("PROXY_OPEN") and isinstance(exception, TunnelError):
                oldProxyString = request.meta["proxy"]
                ApeProxyManager.removeBadProxy(oldProxyString)
                proxyString = ApeProxyManager.getProxy()['string']
                request.meta["proxy"] = proxyString
                logging.warning('代理异常，切换代理(%s)第 %d 次重试中(%s)' % (proxyString, retries, request.url))
            else:
                logging.warning('未启用代理或网络异常与代理无关，第 %d 次重试中(%s)' % (retries, request.url))
            self.save_url(request, spider)
            return self._retry(request, exception, spider)

    def save_url(self, request, spider):
        '''
        当前重试次数已经超过了最大重试次数，修改代理
        :param request:
        :return:
        '''
        retries = request.meta.get('retry_times', 0) + 1
        if retries > self.max_retry_times:
            key = request.cb_kwargs
            logging.warning("连续请求%s次，放弃请求" % str(retries))
            if spider.name == SpiderTypeEnum.PATENT.value:
                if key['requestType'] == 'PatentGetFirstPage':
                    ErrorUtil.markCodeError(type=SpiderTypeEnum.PATENT, code=key['code'], date=key['date'])
                # elif key['requestType'] == 'PatentGetLinks':
                #     ErrorUtil.markPageError(type=SpiderTypeEnum.PATENT, code=key['code'], date=key['date'],
                #                             pagenum=key['pagenum'])
                elif key['requestType'] == "patentGetContent":
                    ErrorUtil.markLinkError(type=SpiderTypeEnum.PATENT, url=key['url'], date=key['date'], code=key['code'])
            elif spider.name == SpiderTypeEnum.PAPER_AND_ACH.value:
                if key['requestType'] == "PaperAchGetFirstPage":
                    ErrorUtil.markCodeError(type=SpiderTypeEnum.PAPER_AND_ACH, code=key['code'], date=key['date'])
                # elif key['requestType'] == 'PaperAchGetLinks':
                #     ErrorUtil.markPageError(type=SpiderTypeEnum.PAPER_AND_ACH.value, code=key['code'], date=key['date'],
                #                             pagenum=key['pagenum'])
                elif key['requestType'] == "JournalGetContent":
                    ErrorUtil.markLinkError(type=SpiderTypeEnum.JOURNAL, url=key['url'], date=key['date'], code=key['code'])
                elif key['requestType'] == "BoshuoGetContent":
                    ErrorUtil.markLinkError(type=SpiderTypeEnum.BOSHUO, url=key['url'], date=key['date'], code=key['code'])
                elif key['requestType'] == "AchGetContent":
                    ErrorUtil.markLinkError(type=SpiderTypeEnum.ACHIEVEMENT, url=key['url'], date=key['date'], code=key['code'])


