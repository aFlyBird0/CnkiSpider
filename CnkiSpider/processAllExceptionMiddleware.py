from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from scrapy.http import HtmlResponse
from twisted.web.client import ResponseFailed
from scrapy.core.downloader.handlers.http11 import TunnelError
from CnkiSpider.file_util import FileUtil
from CnkiSpider.commonUtils import SpiderTypeEnum, ErrorUtil


class ProcessAllExceptionMiddleware(object):
    ALL_EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
                      ConnectionRefusedError, ConnectionDone, ConnectError,
                      ConnectionLost, TCPTimedOutError, ResponseFailed,
                      IOError, TunnelError)

    # def process_response(self, request, response, spider):
    #     # 捕获状态码为40x/50x的response
    #     if str(response.status).startswith('4') or str(response.status).startswith('5'):
    #         # 随意封装，直接返回response，spider代码中根据url==''来处理response
    #         response = HtmlResponse(url='')
    #         return response
    #     # 其他状态码不处理
    #     return response



    def process_exception(self, request, exception, spider):
        # 捕获几乎所有的异常
        if isinstance(exception, self.ALL_EXCEPTIONS):
            # 在日志中打印异常类型
            print('Got exception: %s' % (exception))
            # 随意封装一个response，返回给spider
            response = HtmlResponse(url='exception')
            return response
        # 打印出未捕获到的异常
        print('not contained exception: %s' % exception)

    def process_response(self, request, response, spider):
        if str(response.status).startswith('4') or str(response.status).startswith('5'):
            # # 随意封装，直接返回response，spider代码中根据url==''来处理response
            key = request.cb_kwargs
            # print(request)
            if spider.name == SpiderTypeEnum.PATENT.value:
                # print(key)
                if key['requestType'] == 'PatentGetFirstPage':
                    print('请求状态:%s' % response.status)
                    print('请求链接:%s' % response.meta['url'])
                    print('响应内容:%s' % response.text)
                    ErrorUtil.markDayError(type=SpiderTypeEnum.PATENT.value, code=key['code'], date=key['date'])
                elif key['requestType'] == 'PatentGetLinks':
                    ErrorUtil.markPageError(type=SpiderTypeEnum.PATENT.value, code=key['code'], date=key['date'],
                                       pagenum=key['pagenum'])
                elif key['requestType'] == "patentGetContent":
                    ErrorUtil.markLinkError(type=SpiderTypeEnum.PATENT.value, url=key['url'])
                else:
                    print('这传的什么jb玩意？')
                # self.markFirstError(key['code'], key['date'], pagenum)
            elif 'error' in spider.name:
                if 'pagenum' in key:
                    pagenum = key['pagenum']
                else:
                    pagenum = 0
                ErrorUtil.markSecondError(key['code'], key['date'], pagenum)
            # 返回一个出错的response，前端判断url为空就说明之前的请求有问题
            return HtmlResponse(url='')
        return response


    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
