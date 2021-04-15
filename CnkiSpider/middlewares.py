# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from CnkiSpider.file_util import FileUtil
from CnkiSpider.commonUtils import SpiderTypeEnum


class CnkispiderSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class CnkispiderDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    # def process_exception(self, request, exception, spider):
    #     # Called when a download handler or a process_request()
    #     # (from other downloader middleware) raises an exception.
    #
    #     # Must either:
    #     # - return None: continue processing this exception
    #     # - return a Response object: stops process_exception() chain
    #     # - return a Request object: stops process_exception() chain
    #     pass

    # 全局请求异常处理
    def process_exception(self, request, exception, spider):
        key = request.cb_kwargs
        print('全局异常拦截！！！\n')
        print(exception)
        if spider.name == SpiderTypeEnum.PATENT.value:
            print(key)
            if key['requestType'] == 'PatentGetFirstPage':
                self.markDayError(type=SpiderTypeEnum.PATENT.value, code=key['code'], date=key['date'])
            elif key['requestType'] == 'PatentGetLinks':
                self.markPageError(type=SpiderTypeEnum.PATENT.value, code=key['code'], date=key['date'], pagenum=key['pagenum'])
            elif key['requestType'] == "patentGetContent":
                self.markLinkError(type=SpiderTypeEnum.PATENT.value, url=key['url'])
            else:
                print('这传的什么jb玩意？')
            # self.markFirstError(key['code'], key['date'], pagenum)
        elif 'error' in spider.name:
            if 'pagenum' in key:
                pagenum = key['pagenum']
            else:
                pagenum = 0
            self.markSecondError(key['code'], key['date'], pagenum)
        elif spider.name == 'link':
            self.markLinkError(key['url'], spider.name)
        return request

    def markLinkError(self, url, type):
        with open(FileUtil.errorLinkDir + type + 'Error.txt', 'a', encoding='utf-8') as file:
            file.write(url + '\n')

    def markSecondError(self, code, date, pagenum):
        if pagenum == 0:
            with open('error/erday.txt', 'a', encoding='utf-8') as f:
                f.write(code + '&' + date + '\n')
        else:
            with open('error/erpage.txt', 'a', encoding='utf-8') as f:
                f.write(code + '&' + date + '&' + str(pagenum) + '\n')

    def markFirstError(self, code, date, pagenum):
        if pagenum == 0:
            with open('error/errorday_' + date + '.txt', 'a', encoding='utf-8') as f:
                f.write(code + '&' + date + '\n')
        else:
            with open('error/errorpage_' + date + 'txt', 'a', encoding='utf-8') as f:
                f.write(code + '&' + date + '&' + str(pagenum) + '\n')

    def easyErrorRecoder(self, url):
        with open('error/EasyErrorRecorder.txt', 'a', encoding='utf-8') as file:
            file.write(url + '\n')

    def markDayError(self, type, code, date):
        with open(FileUtil.errorDayDir + type +  '.txt', 'a', encoding='utf-8') as f:
            f.write(code + '&' + date + '\n')

    def markPageError(self, type, code, date, pagenum):
        with open(FileUtil.errorPageDir + type +  '.txt', 'a', encoding='utf-8') as f:
            f.write(code + '&' + date + '&' + str(pagenum) + '\n')

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)