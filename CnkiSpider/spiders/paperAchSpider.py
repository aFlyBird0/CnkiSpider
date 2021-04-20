import datetime
import math
import re
import time
import uuid

import requests
import scrapy

from CnkiSpider.items import *
from CnkiSpider.statusManager import StatusManager
from CnkiSpider.commonUtils import StringUtil, SpiderTypeEnum, CookieUtil, ErrorUtil
from CnkiSpider.file_util import FileUtil
import os
import logging

class PaperAchSpider(scrapy.Spider):
    '''
    博硕、期刊、科技成果都在这个spider里面
    '''
    name = 'paperAch'
    allowed_domains = ['kns.cnki.net']
    custom_settings = {
        # 设置管道下载
        # 设置log日志
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': FileUtil.logDir + 'paperAch.log'
    }

    def __init__(self, settings, *args, **kwargs):
        super(PaperAchSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://kns.cnki.net/kns/brief/brief.aspx?RecordsPerPage=50&QueryID=33&ID=&turnpage=1&tpagemode=L&dbPrefix=SCDB&Fields=&DisplayMode=listmode&PageName=ASP.brief_result_aspx&isinEn=1&curpage='

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(crawler.settings, *args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    # 重写startrequests
    def start_requests(self):

        FileUtil.initOutputDir()
        sm = StatusManager(SpiderTypeEnum.PAPER_AND_ACH)
        lastDateAndCode = sm.getLastDateAndCode()
        if lastDateAndCode is None:
            return
        # 上次爬取可能进行到了一半，所以要重爬一下
        nextDateAndCode = lastDateAndCode
        while nextDateAndCode is not None:
            date = nextDateAndCode[0]
            code = nextDateAndCode[1]
            logging.info("开始爬取论文和成果链接,日期：%s，学科分类：%s" % (date, code))
            # 根据日期、code获取cookies
            cookies = CookieUtil.getPaperAchCookiesProxy(date,code)
            url_first = self.base_url + '1'
            yield scrapy.Request(
                url=url_first,
                cookies=cookies,
                callback=self.parse_first_page,
                cb_kwargs={
                    'cookies': cookies,
                    "code": code,
                    "date": date,
                    "requestType": "PaperAchGetFirstPage"
                },
                meta={
                    'url': url_first,
                    "requestType": "PaperAchGetFirstPage"
                },
                dont_filter=True
            )
            nextDateAndCode = sm.getNextDateAndCode()
        logging.info('所有论文成果链接已经获取结束！')

    # 第一页内容解析，获取页数信息
    def parse_first_page(self,response,cookies,code,date):
        if ErrorUtil.isBadResponse(response=response):
            return
        cookies_now = cookies
        pagerTitleCell = response.xpath('//div[@class="pagerTitleCell"]/text()').extract_first()
        if pagerTitleCell == None:
            logging.info(response.text)
            logging.info(response.text)
            self.markFirstError(code,date,0)
            return
        page = pagerTitleCell.strip()
        num = int(re.findall(r'\d+', page.replace(',', ''))[0]) # 文献数
        pagenum = math.ceil(num / 50)  #算出页数
        logging.info("%s %s 共有：%d篇文献, %d页" % (code,date,num,pagenum))
        if num < 1:
            return
        if pagenum > 120:
            with open(FileUtil.errorOverflowDir + 'papentOverflow.txt', 'a') as f:
                f.write(date + ':' + code + '\n')
            return
        for i in range(1,pagenum+1):
            if i % 13 == 0:
                cookies_now = CookieUtil.getPaperAchCookiesProxy(date,code) # 超过15页换cookie
            url = self.base_url + str(i)
            yield scrapy.Request(
                url=url,
                cookies=cookies_now,
                callback=self.parse_page_links,
                cb_kwargs={
                    "pagenum": i,
                    "code": code,
                    "date": date,
                    "requestType": "PaperAchGetLinks"
                },
                meta={
                    'url': url,
                    "requestType": "PaperAchGetLinks"
                },
                dont_filter=True
            )

    # 解析列表内容获取链接
    def parse_page_links(self,response,pagenum,code,date):
        if ErrorUtil.isBadResponse(response=response):
            return
        rows = response.xpath('//table[@class="GridTableContent"]/tr')
        if len(rows) < 1:
            # 某一页没有获取到列表内容
            logging.error('页面无链接，以下是获取到的response:', response.text)
            self.markFirstError(code,date,pagenum)
            return
        else:
            rows.pop(0) # 去掉标题行
            num = len(rows) # 该页链接数
            logging.info("爬取%s %s 第%d页: %d个链接" % (code,date,pagenum,num))
            for row in rows:
                link = row.xpath('./td/a[@class="fz14"]/@href').extract_first()
                link_params = link.split('&')
                urlParam = link_params[3] + "&" + link_params[4] + "&" + link_params[5]
                url = 'https://kns.cnki.net/KCMS/detail/detail.aspx?' + urlParam
                db = row.xpath('./td')[5].xpath('./text()').extract_first().strip()
                if db == '期刊':
                    item = JournalLinkItem()
                    item['code'] = code
                    item['url'] = url
                    item['db'] = db
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_journal_content,
                        dont_filter=True,
                        cb_kwargs={
                            'url': url,
                            'code': code,
                            'date': date,
                            "requestType": "JournalGetContent"
                        },
                        meta={
                            'url': url,
                            "requestType": "JournalGetContent"
                        }
                    )
                elif db == '博士' or db == '硕士':
                    item = BoshuoLinkItem()
                    item['code'] = code
                    item['url'] = url
                    item['db'] = db
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_boshuo_content,
                        dont_filter=True,
                        cb_kwargs={
                            'url': url,
                            'code': code,
                            'date': date,
                            "requestType": "BoshuoGetContent"
                        },
                        meta={
                            'url': url,
                            "requestType": "JournalGetContent"
                        }
                    )
                elif db == '科技成果':
                    item = AchLinkItem()
                    item['code'] = code
                    item['url'] = url
                    item['db'] = db
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_ach_content,
                        dont_filter=True,
                        cb_kwargs={
                            'url': url,
                            'code': code,
                            'date': date,
                            "requestType": "AchGetContent"
                        },
                        meta={
                            'url': url,
                            "requestType": "JournalGetContent"
                        }
                    )


    # 获取期刊详情页内容
    def parse_journal_content(self, response, url, code, date, requestType):
        # 跳过知网错误链接
        # if url == 'https://kns.cnki.net/KCMS/detail/Error.aspx':
        #     return
        if ErrorUtil.isBadResponse(response=response):
            return
        logging.info("解析期刊：%s" % url)
        item = self.getDefaultJournalItem()
        item = JournalContentItem()
        item['naviCode'] = code
        item['type'] = SpiderTypeEnum.JOURNAL.value
        item['year'] = date[0:4]
        item['url'] = url
        # 根据link链接生成唯一uid，散列是SHA1，去除-
        uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, url))
        suid = ''.join(uid.split('-'))
        item['uid'] = suid
        item['title'] = response.xpath('//h1/text()').extract_first()
        magazine = response.xpath('//div[@class="top-tip"]/span/a')
        magazinefunc = magazine.xpath('./@onclick').extract_first()
        m = magazinefunc.strip().split("'")
        item['magazine'] = magazine.xpath('./text()').extract_first() + "-pcode=" + m[1] + "&pykm=" + m[3]
        summary = response.xpath('string(//span[@id="ChDivSummary"])').extract_first()
        item['summary'] = summary.replace('\n', '').replace('\r', ' ')
        keywordsfuncs = response.xpath('//p[@class="keywords"]/a/@onclick').extract()
        if len(keywordsfuncs) > 0:
            keywords = ""
            for k in keywordsfuncs:
                k = k.strip().split("'")
                keywords = keywords + ";" + k[3] + "-" + k[7]
            item['keywords'] = keywords[1:]
        item['authorsWithCode'] = self.getAuthorsWithLinkStr(response)
        item['authors'] = "&&".join(self.getAuthorsList(response))
        # 单位字符串用';'分隔
        organs = ";".join(self.getOrganList(response))
        item['organs'] = organs
        item['authorOrganJson'] = self.getAuthorOrganJson(response)
        top_space = response.xpath('//li[@class="top-space"]')
        for space in top_space:  # 存在不同文献格式不同，只能判断标题名称
            title = space.xpath('./span/text()').extract_first()
            content = space.xpath('./p/text()').extract_first()
            if title == 'DOI：':
                item['DOI'] = content
            if title == '分类号：':
                item['cate_code'] = content
            if title == '来源数据库：':
                item['db'] = content
            if title == '专辑：':
                item['special'] = content
            if title == '专题：':
                item['subject'] = content
        # 保存html文件
        FileUtil.saveHtml(response=response, type=SpiderTypeEnum.JOURNAL.value, url=url, title=item['title'], year=date[0:4])
        yield item

    # 获取博硕详情页内容
    def parse_boshuo_content(self, response, url, code, date, requestType):
        # if url == 'https://kns.cnki.net/KCMS/detail/Error.aspx':
        #     return
        if ErrorUtil.isBadResponse(response=response):
            return
        logging.info("解析期刊：%s" % url)
        item = self.getDefaultBoshuoItem()
        # 跳过知网错误链接
        item['naviCode'] = code
        item['type'] = SpiderTypeEnum.BOSHUO.value
        item['year'] = date[0:4]
        # 无用字段，为了让期刊和博硕的数据格式保持一致
        item['authorsWithCode'] = ""
        item['url'] = url
        # 根据link链接生成唯一uid，散列是SHA1，去除-
        uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, url))
        suid = ''.join(uid.split('-'))
        item['uid'] = suid
        item['title'] = response.xpath('//div[@class="wx-tit"]/h1/text()').extract_first()
        summary = response.xpath('//span[@id="ChDivSummary"]/text()').extract_first()
        if summary:
            item['summary'] = summary.replace('\n', '').replace('\r', ' ')
        keywordsfuncs = response.xpath('//div[@class="brief"]/div/p[@class="keywords"]/a/@onclick').extract()
        keywords = ""
        for k in keywordsfuncs:
            k = k.strip().split("'")
            keywords = keywords + ";" + k[3] + "-" + k[7]
        item['keywords'] = keywords[1:]
        brief = response.xpath('//div[@class="wx-tit"]/h3/span')
        splitTag = "&&"  # 作者分隔符
        if (len(brief) >= 2):
            authors = brief[0]
            if authors.xpath('./a'):
                authorfuncs = authors.xpath('./a/@onclick').extract()
                authors = ""
                for a in authorfuncs:
                    a = a.strip().split("'")
                    author = a[3] + '-' + a[5]
                    authors = authors + splitTag + author
                    # 去除第一个多余拆分隔符的影响
                item['authors'] = authors[len(splitTag):]
            else:
                item['authors'] = authors.xpath('./text()').extract_first() + "-null"
            school = brief[1]
            if school.xpath('./a'):
                item['organs'] = school.xpath('./a/text()').extract_first().strip()
            else:
                item['organs'] = school.xpath('./text()').extract_first()

        authorOrganJson = {}
        author = item['authors'].split("-")[0]
        authorOrganJson[author] = [item['organs']]
        item['authorOrganJson'] = str(authorOrganJson)
        top_space = response.xpath('//li[@class="top-space"]')
        for space in top_space:  # 存在不同文献格式不同，只能判断标题名称
            title = space.xpath('./span/text()').extract_first()
            content = space.xpath('./p/text()').extract_first()
            if title == 'DOI：':
                item['DOI'] = content
            if title == '来源数据库：':
                item['db'] = content
            if title == '专辑：':
                item['special'] = content
            if title == '专题：':
                item['subject'] = content
            if title == '分类号：':
                item['cate_code'] = content
        rows = response.xpath('//div[@class="row"]')
        for row in rows:
            title = row.xpath('./span/text()').extract_first()
            if title == '导师：':
                if row.xpath('./p/a'):
                    mentorfuncs = row.xpath('./p/a/@onclick').extract_first()
                    m = mentorfuncs.strip().split("'")
                    item['mentor'] = m[3] + '-' + m[5]
                else:
                    item['mentor'] = row.xpath('./p/text()').extract_first()
        # 保存html文件
        FileUtil.saveHtml(response=response, type=SpiderTypeEnum.BOSHUO.value, url=url, title=item['title'], year=date[0:4])
        yield item

    # 获取成果详情页内容
    def parse_ach_content(self, response, url, code, date, requestType):
        # 跳过知网错误链接
        # if url == 'https://kns.cnki.net/KCMS/detail/Error.aspx':
        #     return
        if ErrorUtil.isBadResponse(response=response):
            return
        logging.info("解析期刊：%s" % url)
        item = self.getDefaultAchItem()
        item['naviCode'] = code
        item['type'] = SpiderTypeEnum.ACHIEVEMENT.value
        item['year'] = date[0:4]
        item['url'] = url
        # 根据link链接生成唯一uid，散列是SHA1，去除-
        uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, url))
        suid = ''.join(uid.split('-'))
        item['uid'] = suid
        item['title'] = response.xpath('//h1/text()').extract_first()
        rows = response.xpath('//div[@class="row"]')
        for row in rows:
            title = row.xpath('./span/text()').extract_first()
            content = row.xpath('./p/text()').extract_first()
            if title == '成果完成人：':
                item['authors'] = content.replace(";", "&&")
            if title == '第一完成单位：':
                item['organ'] = content
            if title == '关键词：':
                item['keywords'] = content
            if title == '中图分类号：':
                item['book_code'] = content
            if title == '学科分类号：':
                item['subject_code'] = content
            if title == '成果简介：':
                item['summary'] = content.replace('\n', '').replace('\r', ' ')
            if title == '成果类别：':
                item['category'] = content
            if title == '成果入库时间：':
                item['in_time'] = content
            if title == '成果水平：':
                item['level'] = content
            if title == '研究起止时间：':
                item['pass_time'] = content
            if title == '评价形式：':
                item['evaluate'] = content
        # 保存html文件
        FileUtil.saveHtml(response=response, type=SpiderTypeEnum.ACHIEVEMENT.value, url=url, title=item['title'], year=date[0:4])
        yield item

    def getDefaultJournalItem(self):
        '''
        为期刊item加默认的键，防止后面保存出现不存在的键
        :param item:
        :return:
        '''
        item = JournalContentItem()
        item['naviCode'] = ""  # 学科分类代码 如A001这种
        item['type'] = ""
        item['year'] = ""
        item['url'] = ""
        item['uid'] = ""
        item['title'] = ""
        item['authors'] = ""  # 纯作者名列表
        item['authorsWithCode'] = ""  # 带作者code的作者列表
        item['organs'] = ""
        item['authorOrganJson'] = ""  # 作者和单位的对应关系json字符串
        item['summary'] = ""
        item['keywords'] = ""
        item['DOI'] = ""
        item['special'] = ""  # 专辑
        item['subject'] = ""  # 专题
        item['cate_code'] = ""  # 分类号
        item['db'] = ""  # 来源数据库

        item['magazine'] = ""  # 期刊
        item['mentor'] = ""  # 博硕导师
        return item

    def getDefaultBoshuoItem(self):
        item = BoshuoContentItem()
        item = JournalContentItem()
        item['naviCode'] = ""  # 学科分类代码 如A001这种
        item['type'] = ""
        item['year'] = ""
        item['url'] = ""
        item['uid'] = ""
        item['title'] = ""
        item['authors'] = ""  # 纯作者名列表
        item['authorsWithCode'] = ""  # 带作者code的作者列表
        item['organs'] = ""
        item['authorOrganJson'] = ""  # 作者和单位的对应关系json字符串
        item['summary'] = ""
        item['keywords'] = ""
        item['DOI'] = ""
        item['special'] = ""  # 专辑
        item['subject'] = ""  # 专题
        item['cate_code'] = ""  # 分类号
        item['db'] = ""  # 来源数据库

        item['magazine'] = ""  # 期刊
        item['mentor'] = ""  # 博硕导师
        return item

    def getDefaultAchItem(self):
        item = AchContentItem()
        item['naviCode'] = ""  # 学科分类代码 如A001这种
        item['type'] = ""
        item['year'] = ""
        item['url'] = ""
        item['uid'] = ""
        item['title'] = ""
        item['authors'] = ""
        item['organ'] = ""  # 第一完成单位
        item['keywords'] = ""
        item['book_code'] = ""  # 中图分类号
        item['subject_code'] = ""  # 学科分类号
        item['summary'] = ""
        item['category'] = ""  # 成果类别
        item['in_time'] = ""  # 成果入库时间
        item['pass_time'] = ""  # 研究起止时间
        item['level'] = ""  # 成果水平
        item['evaluate'] = ""  # 评价形式
        return item


    # 获得专家（作者）和其链接的字符串
    def getAuthorsWithLinkStr(self, response):
        authorSelector = response.xpath('//h3[@class="author"]/span')

        authors = ""    #作者字符串
        spiltTag = "&&"  # 作者间的分隔符
        for selector in authorSelector:
            if selector.xpath('./a'):
                authorfunc = selector.xpath('./a/@onclick').extract_first()
                a = authorfunc.strip().split("'")
                author = a[3] + "-" + a[5]
            else:
                author = selector.xpath('./text()').extract_first() + "-null"
            # 连接不同的作者，用&&是因为有的作者名中含有&，会导致分离作者名与代码时候产生错误
            authors = authors + spiltTag + author

        return authors[len(spiltTag):]

    #获得专家（作者）列表字符串（无链接）
    def getAuthorsList(self, response):
        authorSelector = response.xpath('//h3[@class="author"]/span')

        authors = []    #作者列表
        for selector in authorSelector:
            if selector.xpath('./a'):
                authorfunc = selector.xpath('./a/@onclick').extract_first()
                a = authorfunc.strip().split("'")
                author = a[3]
            else:
                author = selector.xpath('./text()').extract_first()
            authors.append(author)
        return authors

    # 得到形如 '杭电;浙大;清华大学' 形式的单位字符串
    # 这个是原先的方式，单位顺序会乱掉，已舍弃
    # 已舍弃
    def getOrganStrOld(self, response):
        organstr = ""
        organSelector = response.xpath('//div[@class="wx-tit"]/h3')[1]
        if organSelector.xpath('./a[@class="author"]'):
            organ_a = organSelector.xpath('./a[@class="author"]/text()').extract()
            for o in organ_a:
                organstr = organstr + o.strip()
        # organ_noa = organSelector.xpath('./span/text()').extract_first()
        organ_noa = organSelector.xpath('./text()').extract_first()
        if organ_noa:
            organstr = organstr + organ_noa
        nonum = (re.sub(r'(\d+)', ' ', organstr)).strip()
        organlist = nonum.strip('.').split('.')
        organs = ""
        spiltTag = ';' # 单位间的分隔符
        for organ in organlist:
            organs = organs + spiltTag + organ.strip()
        # 规避掉开头多余的分隔符
        return organs[len(spiltTag):]

    # 得到单位的列表[杭电,浙大,清华大学]，正序版
    def getOrganList(self, response):
        organSelector = response.xpath('//div[@class="wx-tit"]/h3')[1]
        # 这里简化了原来的代码，针对有链接和无链接的单位，用一个或逻辑，
        # 有链接的提取a标签下的，没链接的直接就是text()，这样的话顺序是对的
        # 注意单位有的是嵌套在span下的，有的没有span
        xpathStr = './span/a[@class="author"]/text() | ./span/text() | ./a[@class="author"]/text() | ./text()'
        organs = organSelector.xpath(xpathStr).extract()
        # 存在一个text()中两个单位的情况，需要处理一下
        organStr = "".join(organs)
        # for organ in organs:
        #     # 去除'数字.'
        #     organList.append(re.sub(r'(\d+)\.', ' ', organ).strip())
        organsWithoutNum = (re.sub(r'(\d+)', ' ', organStr)).strip()
        organList = organsWithoutNum.strip('.').split('.')
        return organList

    # 生成作者和单位相对应的json
    def getAuthorOrganJson(self, response):
        # authorSelector = response.xpath('//h3[@class="author"]/span')
        # organSelector = response.xpath('//div[@class="wx-tit"]/h3')[1]
        authorOrganDict = {} # 专家和单位的对应字典，后面转成json
        # 作者列表
        authorList = self.getAuthorsList(response)
        # 如果作者代码块中没有出现sup，即无上标，说明所有人在同一个单位
        if not response.xpath('//h3[@class="author"]/span//sup').extract_first():
            # 得到形如 '杭电;浙大;清华大学' 形式的单位字符串
            # 但由于没有上标，单位应该只有一个，所以这里其实单位是单独的
            organStr = self.getOrganList(response)
            # 为每一个作者添加单位信息
            for author in authorList:
                authorOrganDict[author] = organStr
        else:
            # 得到所有的下标，按顺序和作者对应就能得到每个作者与某个单位的对应关系
            # 结果示例：['1', '1', '1', '1,2']
            # 下面用span，不能用a,有的人是没有链接的
            subs = response.xpath('//h3[@class="author"]/span//sup/text()').extract()
            # 得到形如 '杭电;浙大;清华大学' 形式的单位字符串，再转换成列表
            organList = self.getOrganList(response)
            # 遍历专家列表，并取出同index的sub列表，利用sub中存储的下标在单位列表中找到对应
            for i in range(len(authorList)):
                # 每个作者可能属于多个单位
                organListOneAuthor = []
                # logging.debug(subs, i)
                # logging.debug(organList)
                # logging.debug(authorList)
                for index in subs[i].split(','):
                    # 这里注意index要减1，因为知网上标是从1开始，列表是从0开始
                    try:
                        organListOneAuthor.append(organList[int(index)-1])
                    except IndexError as e:
                        # 这段异常调试代码已经找到了数组越界成因，主要是之前单位字段提取有点问题
                        logging.error('异常来啦！')
                        logging.error('标题', response.xpath('//h1/text()').extract_first())
                        logging.error('上标列表', subs)
                        logging.error('目前上标', index)
                        logging.error('单位列表', organList)
                        logging.error('作者列表', authorList)
                        # 重新抛出
                        raise e
                authorOrganDict[authorList[i]] = organListOneAuthor
        return str(authorOrganDict)

    def markFirstError(self, code, date, pagenum):
        if pagenum == 0:
            with open('error/errorday_' + date + '.txt', 'a', encoding='utf-8') as f:
                f.write(code + '&' + date + '\n')
        else:
            with open('error/errorpage_' + date + '.txt', 'a', encoding='utf-8') as f:
                f.write(code + '&' + date + '&' + str(pagenum) + '\n')
