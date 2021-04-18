import scrapy
import time
import math
import re
import requests
from CnkiSpider.items import PatentContentItem
from CnkiSpider.items import ErrorUrlItem
from CnkiSpider.commonUtils import StringUtil
from CnkiSpider.statusManager import StatusManager
from CnkiSpider.commonUtils import SpiderTypeEnum
from CnkiSpider.file_util import FileUtil
from CnkiSpider.proxy import ProxyManager
from scrapy.http.cookies import CookieJar
from CnkiSpider.proxy import ProxyManager

import logging
import datetime


class PatentSpider(scrapy.Spider):
    name = 'patent'
    allowed_domains = ['www.cnki.net/']
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
        sm = StatusManager(SpiderTypeEnum.PATENT)
        lastDateAndCode = sm.getLastDateAndCode()
        if lastDateAndCode is None:
            return
        # 上次爬取可能进行到了一半，所以要重爬一下
        nextDateAndCode = lastDateAndCode
        while nextDateAndCode is not None:
            date = nextDateAndCode[0]
            code = nextDateAndCode[1]
            logging.info("开始爬取专利链接,日期：%s，学科分类：%s" % (date, code))
            # cookies = self.getCookies(date, code)

            url_first = 'https://kns.cnki.net/kns/brief/brief.aspx?curpage=%d&RecordsPerPage=50&QueryID=10&ID=&turnpage=1&tpagemode=L&dbPrefix=SCPD&Fields=&DisplayMode=listmode&PageName=ASP.brief_result_aspx&isinEn=0&' % 1

            yield scrapy.Request(
                url=url_first,
                # cookies=cookies,
                callback=self.parse_first_page,
                cb_kwargs={
                    # 'cookies': cookies,
                    "code": code,
                    "date": date,
                    "requestType": 'PatentGetFirstPage'
                },
                meta={
                    'url': url_first,
                    "requestType": 'PatentGetFirstPage'
                },
                dont_filter=True
            )
            nextDateAndCode = sm.getNextDateAndCode()
        logging.info('所有专利链接已经获取结束！')

    # 第一页内容解析，获取页数信息
    def parse_first_page(self, response,code, date,requestType):
        if self.generateErrorItem(response=response):
            return
        # cookies_now = cookies
        pagerTitleCell = response.xpath('//div[@class="pagerTitleCell"]/text()').extract_first()
        if pagerTitleCell == None:
            print(response.text)
            logging.error("论文页面解析出现错误", code, date, response.meta['url'], response.text)
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
        for i in range(1, pagenum + 1):
            if i % 13 == 0:
                # cookies_now = self.getCookies(date, code)  # 超过15页换cookie
                pass
            url =  self.base_url % i
            # print(url)
            yield scrapy.Request(
                url=url,
                # cookies=cookies_now,
                callback=self.parse_page_links,
                cb_kwargs={
                    "pagenum": i,
                    "code": code,
                    "date": date,
                    "requestType": "PatentGetLinks"
                },
                meta={
                    'url':url,
                    "requestType": "PatentGetLinks"
                },
                dont_filter=True
            )

    def parse_page_links(self,response,pagenum,code,date,requestType):
        if self.generateErrorItem(response=response):
            return
        link = response.xpath('//a[@class="fz14"]/@href').extract()  # 返回链接地址href列表
        if len(link) == 0:
            return
        logging.info("日期：%s,学科分类：%s，第%d页有%d个专利" % (date, code, pagenum+1, len(link)))
        for j in range(len(link)):
            # item = PatentCodeItem()
            patentCode = re.search(r'filename=(.*)$', link[j]).group(1)
            # item['patentCode'] = patentCode
            # yield item
            url = self.patent_content_pre_url % (date[0:4], patentCode)
            # cookies = self.getCookies(date, code)
            # print(date)
            yield scrapy.Request(
                url=url,
                # cookies=cookies,
                callback=self.parse_content,
                dont_filter=True,
                cb_kwargs={
                    'url': url,
                    'code': code,
                    'date': date,
                    "requestType": "patentGetContent"
                },
                meta={
                    'url':url,
                    "requestType": "patentGetContent"
                }
            )

    # 获取专利详情页内容
    def parse_content(self, response, url, code, date, requestType):
        if self.generateErrorItem(response=response):
            return
        logging.info("解析专利：%s" % url)
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
    def getCookies(self, date, code, proxy = None):
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



    def generateErrorItem(self, response):
        '''
        判断是否出现错误，如果有错误，yield错误item，并返回出错标志
        :param response:
        :return:
        '''
        item = ErrorUrlItem()
        item['url'] = response.meta['url']
        item['reqType'] = response.meta['requestType']
        errorFlag = False
        if not response.url:  # 接收到url==''时
            logging.info('500')
            item['errType'] = '500'
            errorFlag = True
            yield item
        elif 'exception' in response.url:
            item = ErrorUrlItem()
            item['errType'] = 'Exception'
            errorFlag = True
            yield item
        return errorFlag
