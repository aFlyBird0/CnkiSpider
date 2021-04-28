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

import logging
import datetime


class PatentSpider(RedisSpider):
    name = 'patent'
    allowed_domains = ['www.cnki.net', 'kns.cnki.net']
    # start_urls = ['//https://www.cnki.net//']
    custom_settings = {
        # 设置管道下载
        # 设置log日志
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': FileUtil.logDir + 'patent.log'
    }

    def __init__(self, settings, *args, **kwargs):
        super(PatentSpider, self).__init__(*args, **kwargs)
        # self.base_url = 'http://dbpub.cnki.net/grid2008/dbpub/detail.aspx?dbcode=scpd&'
        self.base_url = 'https://kns.cnki.net/kns/brief/brief.aspx?curpage=%d&RecordsPerPage=50&QueryID=10&ID=&turnpage=1&tpagemode=L&dbPrefix=SCPD&Fields=&DisplayMode=listmode&PageName=ASP.brief_result_aspx&isinEn=0&'
        self.patent_content_pre_url = 'https://kns.cnki.net/kcms/detail/detail.aspx?dbcode=SCPD&dbname=SCPD%s&filename=%s'
        self.sm = StatusManager(SpiderTypeEnum.PATENT)

    # 获取setting中的年份值
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(crawler.settings, *args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    # 重写startrequests
    def start_requests(self):
        FileUtil.initOutputDir()
        # util = PatentUtil()
        # util.generateUrlsDir()
        # dates = util.getAllDayPerYear()

        lastDateAndCode = self.sm.getLastDateAndCode()
        if lastDateAndCode is None:
            return
        # 上次爬取可能进行到了一半，所以要重爬一下
        nextDateAndCode = lastDateAndCode
        while nextDateAndCode is not None:
            date = nextDateAndCode[0]
            code = nextDateAndCode[1]
            logging.info("开始爬取专利链接,日期：%s，学科分类：%s" % (date, code))

            # proxyDict = ApeProxyManager.getProxyDict()
            # proxyString = ApeProxyManager.proxyDict2String(proxyDict)

            url_first = 'https://kns.cnki.net/kns/brief/brief.aspx?curpage=%d&RecordsPerPage=50&QueryID=10&ID=&turnpage=1&tpagemode=L&dbPrefix=SCPD&Fields=&DisplayMode=listmode&PageName=ASP.brief_result_aspx&isinEn=0&' % 1

            if code == self.sm.getCodeFirst():
                # 获取全年信息
                cookiesAllCodeForOneDate = CookieUtil.getPatentCookiesProxy(date, "*")
                yield scrapy.Request(
                    url=url_first,
                    cookies=cookiesAllCodeForOneDate,
                    callback=self.ifSkipDate,
                    cb_kwargs={
                        'cookies': cookiesAllCodeForOneDate,
                        "code": code,
                        "date": date,
                        "requestType": 'PatentIfSkipDate'
                    },
                    meta={
                        'url': url_first,
                        # 'proxy': proxyString,
                        "requestType": 'PatentIfSkipDate'
                    },
                    dont_filter=True
                )

            cookies = CookieUtil.getPatentCookiesProxy(date, code)

            # print("发起请求获取第一页信息", date, code)
            yield scrapy.Request(
                url=url_first,
                cookies=cookies,
                callback=self.parse_first_page,
                cb_kwargs={
                    'cookies': cookies,
                    "code": code,
                    "date": date,
                    "requestType": 'PatentGetFirstPage'
                },
                meta={
                    'url': url_first,
                    # 'proxy': proxyString,
                    "requestType": 'PatentGetFirstPage'
                },
                dont_filter=True
            )
            nextDateAndCode = self.sm.getNextDateAndCode()
        logging.info('所有专利链接已经获取结束！')

        # 获取失败的日期和学科代码，重新获取链接并请求、解析内容
        # self.handleErrorCodeDate()
        # 获取请求失败的链接，重新请求并解析内容
        # self.hanldeErrorLink()


        #################### 重新获取失败的链接，直到所有链接都获取成功 开始 ###################
        logging.info('开始重新获取出错链接并重爬链接')
        errCodeDate = ErrorUtil.getOneErrorCode(type=SpiderTypeEnum.PATENT)
        while errCodeDate:
            id = errCodeDate[0]
            type = errCodeDate[1]
            code = errCodeDate[2]
            date = errCodeDate[3]
            # 从数据库中删除这条已经获取的日期代码对，不用担心出错，如果出错会被错误处理模块捕获
            # 但其实这里还有个小bug，就是可能有的请求还在请求中，但是数据库这时候空了，导致最后几个出错请求没被重新爬
            # 这样的问题就只涉及几个专利，只要再运行一次程序就行
            ErrorUtil.deleteErrorCode(id=id)
            url_first = 'https://kns.cnki.net/kns/brief/brief.aspx?curpage=%d&RecordsPerPage=50&QueryID=10&ID=&turnpage=1&tpagemode=L&dbPrefix=SCPD&Fields=&DisplayMode=listmode&PageName=ASP.brief_result_aspx&isinEn=0&' % 1

            cookies = CookieUtil.getPatentCookiesProxy(date, code)

            # print("发起请求获取第一页信息", date, code)
            yield scrapy.Request(
                url=url_first,
                cookies=cookies,
                callback=self.parse_first_page,
                cb_kwargs={
                    'cookies': cookies,
                    "code": code,
                    "date": date,
                    "requestType": 'PatentGetFirstPage'
                },
                meta={
                    'url': url_first,
                    # 'proxy': proxyString,
                    "requestType": 'PatentGetFirstPage'
                },
                dont_filter=True
            )
            errCodeDate = ErrorUtil.getOneErrorCode(type=SpiderTypeEnum.PATENT)
        logging.info('开始重新获取出错链接并重爬链接')
        ###################################### 重新获取失败的链接，直到所有链接都获取成功 结束################



        ######################## 重新请求所有失败链接 开始 ############################
        logging.info("开始请求失败链接")
        errorLink = ErrorUtil.getOneErrorLink(type=SpiderTypeEnum.PATENT)
        while errorLink:
            id = errorLink[0]
            type = errorLink[1]
            code = errorLink[2]
            link = errorLink[3]
            date = errorLink[4]

            ErrorUtil.deleteErrorLink(id)

            url = link
            yield scrapy.Request(
                url=url,
                # cookies=cookies,
                callback=self.parse_content,
                dont_filter=True,  # 这里不去重，因为之前的链接应该请求过，如果去重再次请求会直接过滤
                cb_kwargs={
                    'url': url,
                    'code': code,
                    'date': date,
                    "requestType": "patentGetContent"
                },
                meta={
                    'url': url,
                    # 'proxy': proxyString,
                    "requestType": "patentGetContent"
                }
            )
            errorLink = ErrorUtil.getOneErrorLink(type=SpiderTypeEnum.PATENT)
        logging.info("所有失败链接已重新请求完毕")
        ######################## 重新请求所有失败链接 结束 ############################

        logging.info("当前（论文）爬取任务、错误重爬均已完成")

    def handleErrorCodeDate(self):
        '''
        重新获取失败的链接，直到所有链接都获取成功 开始
        :return:
        '''
        logging.info('开始重新获取出错链接并重爬链接')
        errCodeDate = ErrorUtil.getOneErrorCode(type=SpiderTypeEnum.PATENT)
        while errCodeDate:
            id = errCodeDate[0]
            type = errCodeDate[1]
            code = errCodeDate[2]
            date = errCodeDate[3]
            # 从数据库中删除这条已经获取的日期代码对，不用担心出错，如果出错会被错误处理模块捕获
            # 但其实这里还有个小bug，就是可能有的请求还在请求中，但是数据库这时候空了，导致最后几个出错请求没被重新爬
            # 这样的问题就只涉及几个专利，只要再运行一次程序就行
            ErrorUtil.deleteErrorCode(id=id)
            url_first = 'https://kns.cnki.net/kns/brief/brief.aspx?curpage=%d&RecordsPerPage=50&QueryID=10&ID=&turnpage=1&tpagemode=L&dbPrefix=SCPD&Fields=&DisplayMode=listmode&PageName=ASP.brief_result_aspx&isinEn=0&' % 1

            cookies = CookieUtil.getPatentCookiesProxy(date, code)

            # print("发起请求获取第一页信息", date, code)
            yield scrapy.Request(
                url=url_first,
                cookies=cookies,
                callback=self.parse_first_page,
                cb_kwargs={
                    'cookies': cookies,
                    "code": code,
                    "date": date,
                    "requestType": 'PatentGetFirstPage'
                },
                meta={
                    'url': url_first,
                    # 'proxy': proxyString,
                    "requestType": 'PatentGetFirstPage'
                },
                dont_filter=True
            )
            errCodeDate = ErrorUtil.getOneErrorCode(type=SpiderTypeEnum.PATENT)
        logging.info('开始重新获取出错链接并重爬链接')
        ###################################### 重新获取失败的链接，直到所以链接都获取成功 结束################

    def hanldeErrorLink(self):
        '''
        重新请求所有失败链接
        :return:
        '''
        logging.info("开始请求失败链接")
        print("我运行了")
        errorLink = ErrorUtil.getOneErrorLink(type=SpiderTypeEnum.PATENT)
        while errorLink:
            id = errorLink[0]
            type = errorLink[1]
            code = errorLink[2]
            link = errorLink[3]
            date = errorLink[4]

            ErrorUtil.deleteErrorLink(id)

            url = link
            yield scrapy.Request(
                url=url,
                # cookies=cookies,
                callback=self.parse_content,
                dont_filter=True,  # 这里不去重，因为之前的链接应该请求过，如果去重再次请求会直接过滤
                cb_kwargs={
                    'url': url,
                    'code': code,
                    'date': date,
                    "requestType": "patentGetContent"
                },
                meta={
                    'url': url,
                    # 'proxy': proxyString,
                    "requestType": "patentGetContent"
                }
            )
            errorLink = ErrorUtil.getOneErrorLink(type=SpiderTypeEnum.PATENT)
        logging.info("所有失败链接已重新请求完毕")




    def ifSkipDate(self, response,code, date,cookies, requestType):
        '''
        判断某天是否有专利，如果没有的话，就直接跳过该天
        :param response:
        :param code:
        :param date:
        :param cookies:
        :param requestType:
        :return:
        '''
        # print('进入parse_first_page成功')
        if ErrorUtil.isBadResponse(response=response):
            return
        # print('进入parse_first_page成功2')
        # 使用上次请求的cookie，否则无法翻页成功
        cookies_now = cookies
        # 获取上次请求的使用的proxy，这次请求用的cookie和proxy都和以前一致
        # proxyString = response.meta['proxy']
        pagerTitleCell = response.xpath('//div[@class="pagerTitleCell"]/text()').extract_first()
        if pagerTitleCell == None:
            # print(response.text)
            # 这里的url一定不是空的，如果是空的话前面已经return了不用担心
            logging.error("专利页面解析出现错误 %s %s %s %s" % (code, date, response.meta['url'], response.text))
            ErrorUtil.markCodeError(code=code, date=date, type=SpiderTypeEnum.PATENT)
            return
        page = pagerTitleCell.strip()
        num = int(re.findall(r'\d+', page.replace(',', ''))[0])  # 文献数
        pagenum = math.ceil(num / 50)  # 算出页数
        logging.info("%s 共有：%d篇文献" % (date, num))
        if num < 1:
            self.sm.stepIntoNextDate(date)
            return

    # 第一页内容解析，获取页数信息
    def parse_first_page(self, response,code, date,cookies, requestType):
        # print('进入parse_first_page成功')
        if ErrorUtil.isBadResponse(response=response):
            return
        # print('进入parse_first_page成功2')
        # 使用上次请求的cookie，否则无法翻页成功
        cookies_now = cookies
        # 获取上次请求的使用的proxy，这次请求用的cookie和proxy都和以前一致
        # proxyString = response.meta['proxy']
        pagerTitleCell = response.xpath('//div[@class="pagerTitleCell"]/text()').extract_first()
        if pagerTitleCell == None:
            # print(response.text)
            # 这里的url一定不是空的，如果是空的话前面已经return了不用担心
            logging.error("专利页面解析出现错误 %s %s %s %s" % (code, date, response.meta['url'], response.text))
            ErrorUtil.markCodeError(code=code, date=date, type=SpiderTypeEnum.PATENT.value)
            return
        page = pagerTitleCell.strip()
        num = int(re.findall(r'\d+', page.replace(',', ''))[0])  # 文献数
        pagenum = math.ceil(num / 50)  # 算出页数
        logging.info("%s %s 共有：%d篇文献, %d页" % (code, date, num, pagenum))
        if num < 1:
            return
        if pagenum > 120:
            with open(FileUtil.errorOverflowDir + 'papentOverflow.txt', 'a') as f:
                f.write(date + ':' + code + '\n')
            return
        # 测试一下cookie一样换proxy行不行的通
        # 后续：测试完成，证明行得通
        # proxyDict = ApeProxyManager.getProxyDict()
        # proxyString = ApeProxyManager.proxyDict2String(proxyDict)
        for i in range(1, pagenum + 1):
            # 超过15页换cookie
            if i % 13 == 0:
                # proxyDict = ApeProxyManager.getProxyDict()
                # proxyString = ApeProxyManager.proxyDict2String(proxyDict)
                cookies_now = CookieUtil.getPatentCookiesProxy(date, code)
            url =  self.base_url % i
            # logging.debug('换了proxy未换cookie看是否能请求成功')
            # logging.debug("发起请求获取第%d页信息 %s %s", (i, date, code))
            yield scrapy.Request(
                url=url,
                cookies=cookies_now,
                callback=self.parse_page_links,
                cb_kwargs={
                    "pagenum": i,
                    "code": code,
                    "date": date,
                    "requestType": "PatentGetLinks"
                },
                meta={
                    'url':url,
                    # 'proxy': proxyString,
                    "requestType": "PatentGetLinks"
                },
                dont_filter=True
            )

    def parse_page_links(self,response,pagenum,code,date,requestType):
        if ErrorUtil.isBadResponse(response=response):
            return
        link = response.xpath('//a[@class="fz14"]/@href').extract()  # 返回链接地址href列表
        if len(link) == 0:
            return
        logging.debug("日期：%s,学科分类：%s，第%d页有%d个专利" % (date, code, pagenum+1, len(link)))
        for j in range(len(link)):
            # item = PatentCodeItem()
            patentCode = re.search(r'filename=(.*)$', link[j]).group(1)
            # item['patentCode'] = patentCode
            # yield item
            url = self.patent_content_pre_url % (date[0:4], patentCode)
            # print(date)
            # proxyDict = ApeProxyManager.getProxyDict()
            # proxyString = ApeProxyManager.proxyDict2String(proxyDict)
            # logging.debug("准备发起解析专利请求,%s" % url)
            yield scrapy.Request(
                url=url,
                # cookies=cookies,
                callback=self.parse_content,
                dont_filter=False, # 这里参与去重，专利文件不重复
                cb_kwargs={
                    'url': url,
                    'code': code,
                    'date': date,
                    "requestType": "patentGetContent"
                },
                meta={
                    'url':url,
                    # 'proxy': proxyString,
                    "requestType": "patentGetContent"
                }
            )

    # 获取专利详情页内容
    def parse_content(self, response, url, code, date, requestType):
        if ErrorUtil.isBadResponse(response=response):
            return
        logging.debug("解析专利：%s" % url)
        item = self.getDefaultPatentItem()
        item['type'] = SpiderTypeEnum.PATENT.value
        item['naviCode'] = code # 学科分类
        item['year'] = date[0:4] # 年份，主要用来爬虫归类用
        title = response.xpath("//h1/text()").extract_first().strip()
        item['title'] = title
        # 有的是在row下，有的是在row的row1和row2下，这么写效率最高
        rows = response.xpath("//div[@class='row'] | //div[@class='row-1'] | //div[@class='row-2']")
        for row in rows:
            key = row.xpath("./span[@class='rowtit']/text() | ./span[@class='rowtit2']/text()").extract_first()
            # 有的文本含有链接，提取方法不一样
            value = row.xpath("./p[@class='funds']/text() | ./p[@class='funds']/a/text()").extract_first()
            if key == "专利类型：":
                item['applicationType'] = value # 专利类型
            elif key == "申请日：":
                item['applicationDate'] = value  # 申请日
            elif key == "多次公布：":
                # 多次公布后面发现是动态加载，其实这样获取不到，但是，不同阶段的专利的申请（专利）号是一样的，多次公布不爬问题也不大
                item['multiPublicationNo'] = value # 多次公布
            elif key == "申请人：":
                item['applicant'] = value   # 申请人
            elif key == "地址：":
                item['applicantAddress'] = value    # 地址
            elif key == "发明人：":
                item['inventors'] = value   # 发明人原始字符串
                i1, i2, i3, i4 = self.getFirstFourAuthor(value)
            elif key == "申请(专利)号：":
                item['applicationNO'] = value  # 申请(专利)号
            elif key == "申请公布号：":
                item['applyPublicationNo'] = value  # 申请公布号
            elif key == "授权公布号：":
                item['authPublicationNo'] =value   # 授权公布号
            elif key == "公开公告日：":
                item['publicationDate'] = value  # 公开公告日 或 授权公告日
            elif key == "授权公告日：":
                item['authPublicationDate'] = value  # 授权公告日
            elif key == "国省代码：":
                item['areaCode'] = value     # 国省代码
            elif key == "分类号：":
                item['classificationNO'] = value    # 分类号
            elif key == "主分类号：":
                item['mainClassificationNo'] = value    # 主分类号
            elif key == "代理机构：":
                item['agency'] = value   # 代理机构
            elif key == "代理人：":
                item['agent'] = value    # 代理人
            elif key == "页数：":
                item['page'] = value # 页数

        abstract = response.xpath("//div[@class='abstract-text']/text()").extract_first()  # 摘要
        sovereignty = response.xpath("//div[@class='claim-text']/text()").extract_first()  # 主权项
        item['abstract'] = StringUtil.stringHanlde(abstract) # 摘要
        item['sovereignty'] = StringUtil.stringHanlde(sovereignty)  # 主权项
        item['url'] = url  # 专利在知网的链接

        # 法律状态 base url
        # legalStatusBaseUrl = "https://kns.cnki.net/kcms/detail/frame/ReaderComments.aspx?flag=gbserach&dbcode=SCPD&dbname=SCPD&filename=%s&vl=%s"
        # 法律状态url中的vl字段
        # vl = response.xpath("//input[@id='listv']/@value").extract_first()
        # item['legalStatus'] = legalStatusBaseUrl % (item['applicationNO'], vl)    # 法律状态链接
        item['legalStatus'] = "" #可以请求旧接口，没必要再爬 https://dbpub.cnki.net/GBSearch/SCPDGBSearch.aspx?ID=
        # 保存html文件
        FileUtil.saveHtml(year=date[0:4], response=response, type=SpiderTypeEnum.PATENT.value, url=url, title=title)
        yield item

    def getDefaultPatentItem(self):
        '''
        为专利item加默认的键，防止后面保存出现不存在的键
        :param item:
        :return:
        '''
        item = PatentContentItem()
        item['naviCode'] = ""
        item['title'] = ""
        item['year'] = ""
        item['applicationType'] = ""
        item['applicationDate'] = ""
        item['multiPublicationNo'] = ""
        item['applicant'] = ""
        item['applicantAddress'] = ""
        item['inventors'] = ""
        item['applicationNO'] = ""
        item['applyPublicationNo'] = ""
        item['publicationDate'] = ""
        item['authPublicationDate'] = ""
        item['authPublicationNo'] = ""
        item['areaCode'] = ""
        item['classificationNO'] = ""
        item['mainClassificationNo'] = ""
        item['agency'] = ""
        item['agent'] = ""
        item['page'] = ""
        item['abstract'] = ""
        item['sovereignty'] = ""
        item['url'] = ""
        item['legalStatus'] = ""
        return item

    def getFirstFourAuthor(self, inventors):
        # 把“叶莉华; 冯洋洋; 王著元; 程志祥; 崔一平”形式的作者划分开
        # 查了下中国专利作者的数量是不受限制的，这里对发明人做了预处理，提取分割了前四位
        first_inventor = inventors.split(';')[0]
        if len(inventors.split(';')) > 1:
            second_inventor = inventors.split(';')[1]
        else:
            second_inventor = ''
        if len(inventors.split(';')) > 2:
            third_inventor = inventors.split(';')[2]
        else:
            third_inventor = ''
        if len(inventors.split(';')) > 3:
            fourth_inventor = inventors.split(';')[3]
        else:
            fourth_inventor = ''

        return first_inventor, second_inventor, third_inventor, fourth_inventor




    # 根据日期，分类代码获取cookies
    # def getCookies(self, date, code, proxy = None):
    #     search_url = 'http://kns.cnki.net/kns/request/SearchHandler.ashx'
    #     times = time.strftime('%a %b %d %Y %H:%M:%S') + ' GMT+0800 (中国标准时间)'
    #     params = {
    #         "action": "",
    #         "NaviCode": code,
    #         "ua": "1.21",
    #         "isinEn": "0",
    #         "PageName": "ASP.brief_result_aspx",
    #         "DbPrefix": "SCPD",
    #         "DbCatalog": "中国专利数据库",
    #         "ConfigFile": "SCPD.xml",
    #         "db_opt": "SCOD",
    #         "db_value": "中国专利数据库",
    #         "date_gkr_from": date,
    #         "date_gkr_to": date,
    #         "his": '0',
    #         '__': times
    #     }
    #     if proxy:
    #         session_response = requests.get(search_url, params=params, proxy=proxy)
    #     else:
    #         session_response = requests.get(search_url, params=params)
    #     cookies = requests.utils.dict_from_cookiejar(session_response.cookies)
    #     return cookies



    def generateErrorItem(self, response):
        '''
        （已弃用）判断是否出现错误，如果有错误，yield错误item，并返回出错标志
        :param response:
        :return:
        '''
        item = ErrorUrlItem()
        item['url'] = response.meta['url']
        item['reqType'] = response.meta['requestType']
        errorFlag = False
        if not response.url:  # 接收到url==''时
            print('这里是异常item url')
            logging.info('500')
            item['errType'] = '500'
            errorFlag = True
            # todo 报错错误item
            # yield item
        elif 'exception' in response.url:
            print('这里是异常item exception')
            item = ErrorUrlItem()
            item['errType'] = 'Exception'
            errorFlag = True
            # todo 保存错误item
            # yield item
        # print('errorFlag', errorFlag)
        return errorFlag


