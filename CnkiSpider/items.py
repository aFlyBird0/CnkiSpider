# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CnkispiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class BoshuoLinkItem(scrapy.Item):
    '''
    博硕
    '''
    url = scrapy.Field()
    db = scrapy.Field()     # 所属数据库
    code = scrapy.Field()   # 学科分类

class JournalLinkItem(scrapy.Item):
    '''
    期刊
    '''
    url = scrapy.Field()
    db = scrapy.Field()     # 所属数据库
    code = scrapy.Field()   # 学科分类

class AchLinkItem(scrapy.Item):
    '''
    科技成果
    '''
    url = scrapy.Field()
    db = scrapy.Field()     # 所属数据库
    code = scrapy.Field()   # 学科分类

class PatentContentItem(scrapy.Item):
    type = scrapy.Field()   #类型，区分是专利还是期刊、博硕、论文
    title = scrapy.Field()  # 标题
    url = scrapy.Field()    # 专利的url
    naviCode = scrapy.Field()   # 学科代码
    year = scrapy.Field()   # 年份, 应该是公开日的年份，仅作爬虫分类用，不一定准确
    applicationType = scrapy.Field()    # 专利类型
    applicationDate = scrapy.Field()    # 申请日
    applyPublicationNo = scrapy.Field()  # 申请公布号
    authPublicationNo = scrapy.Field()  # 授权公布号
    multiPublicationNo = scrapy.Field()  # 多次公布
    publicationDate = scrapy.Field()    # 公开公告日
    authPublicationDate = scrapy.Field()    #授权公告日
    applicant = scrapy.Field()  # 申请人
    applicantAddress = scrapy.Field()   # 地址
    inventors = scrapy.Field()  # 发明人原始字符串
    applicationNO = scrapy.Field()  # 申请(专利)号
    areaCode = scrapy.Field()   # 国省代码
    classificationNO = scrapy.Field()   # 分类号
    mainClassificationNo = scrapy.Field()   # 主分类号
    agency = scrapy.Field() # 代理机构
    agent = scrapy.Field()  # 代理人
    page = scrapy.Field()   # 页数
    abstract = scrapy.Field()   # 摘要
    sovereignty = scrapy.Field()    # 主权项
    legalStatus = scrapy.Field()    # 法律状态

class JournalContentItem(scrapy.Item):
    naviCode = scrapy.Field()   #学科分类代码 如A001这种
    type = scrapy.Field()
    year = scrapy.Field()
    url = scrapy.Field()
    uid = scrapy.Field()
    title = scrapy.Field()
    authors = scrapy.Field()    #纯作者名列表
    authorsWithCode = scrapy.Field()    #带作者code的作者列表
    organs = scrapy.Field()
    authorOrganJson = scrapy.Field()    #作者和单位的对应关系json字符串
    summary = scrapy.Field()
    keywords = scrapy.Field()
    DOI = scrapy.Field()
    special = scrapy.Field() #专辑
    subject = scrapy.Field() #专题
    cate_code = scrapy.Field() #分类号
    db = scrapy.Field() #来源数据库

    magazine = scrapy.Field() # 期刊
    mentor = scrapy.Field() # 博硕导师


class BoshuoContentItem(scrapy.Item):
    naviCode = scrapy.Field()  # 学科分类代码 如A001这种
    type = scrapy.Field()
    year = scrapy.Field()
    url = scrapy.Field()
    uid = scrapy.Field()
    title = scrapy.Field()
    authors = scrapy.Field()    #纯作者名列表
    authorsWithCode = scrapy.Field()    #带作者code的作者列表
    organs = scrapy.Field()
    authorOrganJson = scrapy.Field()  # 作者和单位的对应关系json字符串
    summary = scrapy.Field()
    keywords = scrapy.Field()
    DOI = scrapy.Field()
    special = scrapy.Field()
    subject = scrapy.Field()
    cate_code = scrapy.Field()
    db = scrapy.Field() #来源数据库

    magazine = scrapy.Field() # 期刊
    mentor = scrapy.Field() # 博硕导师


class AchContentItem(scrapy.Item):
    naviCode = scrapy.Field()  # 学科分类代码 如A001这种
    type = scrapy.Field()
    year = scrapy.Field()
    url = scrapy.Field()
    uid = scrapy.Field()
    title = scrapy.Field()
    authors = scrapy.Field()
    organ = scrapy.Field() # 第一完成单位
    keywords = scrapy.Field()
    book_code = scrapy.Field() # 中图分类号
    subject_code = scrapy.Field() # 学科分类号
    summary = scrapy.Field()
    category = scrapy.Field() # 成果类别
    in_time = scrapy.Field() # 成果入库时间
    pass_time = scrapy.Field() # 研究起止时间
    level = scrapy.Field() # 成果水平
    evaluate = scrapy.Field() # 评价形式

class AuthorItem(scrapy.Item):
    code = scrapy.Field()
    name = scrapy.Field()
    school = scrapy.Field()
    category = scrapy.Field()
    upload_amount = scrapy.Field()
    download_amount = scrapy.Field()

class ErrorUrlItem(scrapy.Item):
    url = scrapy.Field()
    errType = scrapy.Field()
    reqType = scrapy.Field()
