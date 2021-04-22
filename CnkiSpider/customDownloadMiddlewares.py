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
                if key['requestType'] == 'PatentGetFirstPage':
                    # print('请求状态:%s' % response.status)
                    # print('请求链接:%s' % response.meta['url'])
                    # print('响应内容:%s' % response.text)
                    ErrorUtil.markDayError(type=SpiderTypeEnum.PATENT.value, code=key['code'], date=key['date'])
                elif key['requestType'] == 'PatentGetLinks':
                    ErrorUtil.markPageError(type=SpiderTypeEnum.PATENT.value, code=key['code'], date=key['date'],
                                       pagenum=key['pagenum'])
                elif key['requestType'] == "patentGetContent":
                    ErrorUtil.markLinkError(type=SpiderTypeEnum.PATENT.value, url=key['url'])
            elif spider.name == SpiderTypeEnum.PAPER_AND_ACH.value:
                if key['requestType'] == "PaperAchGetFirstPage":
                    ErrorUtil.markDayError(type=SpiderTypeEnum.PAPER_AND_ACH.value, code=key['code'], date=key['date'])
                elif key['requestType'] == 'PaperAchGetLinks':
                    ErrorUtil.markPageError(type=SpiderTypeEnum.PAPER_AND_ACH.value, code=key['code'], date=key['date'],
                                            pagenum=key['pagenum'])
                elif key['requestType'] == "JournalGetContent":
                    ErrorUtil.markLinkError(type=SpiderTypeEnum.JOURNAL.value, url=key['url'])
                elif key['requestType'] == "BoshuoGetContent":
                    ErrorUtil.markLinkError(type=SpiderTypeEnum.BOSHUO.value, url=key['url'])
                elif key['requestType'] == "AchGetContent":
                    ErrorUtil.markLinkError(type=SpiderTypeEnum.ACHIEVEMENT.value, url=key['url'])
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
        request.meta["proxy"] = ApeProxyManager.getProxyString()
        request.headers["Proxy-Authorization"] = ApeProxyManager.proxyAuth
        return None




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
            proxyString = ApeProxyManager.getProxyString()
            request.meta["proxy"] = proxyString
            logging.warning('切换代理(%s)重试中(%s)' % (request.url, proxyString))
            self.save_url(request, spider)
            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        if (
            isinstance(exception, self.EXCEPTIONS_TO_RETRY)
            and not request.meta.get('dont_retry', False)
        ):
            logging.warning('错误异常捕捉:%s,开始重试' % exception)
            proxyString = ApeProxyManager.getProxyString()
            request.meta["proxy"] = proxyString
            logging.warning('切换代理(%s)重试中(%s)' % (request.url, proxyString))
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
                    ErrorUtil.markDayError(type=SpiderTypeEnum.PATENT.value, code=key['code'], date=key['date'])
                elif key['requestType'] == 'PatentGetLinks':
                    ErrorUtil.markPageError(type=SpiderTypeEnum.PATENT.value, code=key['code'], date=key['date'],
                                            pagenum=key['pagenum'])
                elif key['requestType'] == "patentGetContent":
                    ErrorUtil.markLinkError(type=SpiderTypeEnum.PATENT.value, url=key['url'])
            elif spider.name == SpiderTypeEnum.PAPER_AND_ACH.value:
                if key['requestType'] == "PaperAchGetFirstPage":
                    ErrorUtil.markDayError(type=SpiderTypeEnum.PAPER_AND_ACH.value, code=key['code'], date=key['date'])
                elif key['requestType'] == 'PaperAchGetLinks':
                    ErrorUtil.markPageError(type=SpiderTypeEnum.PAPER_AND_ACH.value, code=key['code'], date=key['date'],
                                            pagenum=key['pagenum'])
                elif key['requestType'] == "JournalGetContent":
                    ErrorUtil.markLinkError(type=SpiderTypeEnum.JOURNAL.value, url=key['url'])
                elif key['requestType'] == "BoshuoGetContent":
                    ErrorUtil.markLinkError(type=SpiderTypeEnum.BOSHUO.value, url=key['url'])
                elif key['requestType'] == "AchGetContent":
                    ErrorUtil.markLinkError(type=SpiderTypeEnum.ACHIEVEMENT.value, url=key['url'])


