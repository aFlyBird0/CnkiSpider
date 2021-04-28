import pymysql
from CnkiSpider.commonUtils import SpiderTypeEnum
import datetime
import logging
from scrapy.utils.project import get_project_settings

'''
爬虫状态管理工具，主要记录爬到的日期和代码
'''


class StatusManager():



    def __init__(self, type: SpiderTypeEnum):

        self.srcCodeFile = 'dataSrc/codeTest.txt'
        settings = get_project_settings()
        self.host = settings.get("MYSQL_HOST")
        self.port = int(settings.get("MYSQL_PORT"))
        self.user = settings.get("MYSQL_USER")
        self.passwd = settings.get("MYSQL_PASSWD")
        self.database = settings.get("MYSQL_DATABASE")
        self.table = settings.get("STATUS_TABLE")
        # logging.debug(host, port, user, passwd, database, table)

        self.codes = self.getCodeAll()
        self.codeFirst = self.codes[0]
        self.codeLen = len(self.codes)
        self.type = type.value
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user,
                                    passwd=self.passwd, database=self.database)
        self.cursor = self.conn.cursor()
        today = datetime.date.today()
        oneday = datetime.timedelta(days=1)
        self.today = today.strftime('%Y-%m-%d')
        self.yesterday = (today - oneday).strftime('%Y-%m-%d')
        # 默认截止日期是昨天
        self.endDate = None

    def getCodeFirst(self):
        return self.codeFirst

    def getLastDateAndCode(self):
        '''
        从数据库中读取上次爬的日期和学科分类，这次重新爬
        :return:
        '''
        self.cursor.execute("select `curCode`, `curDate`, `endDate` from `%s` where `type` = '%s'" % (self.table, self.type))
        result = self.cursor.fetchone()
        # 数据库没数据就返回空，报错给调用者，提示用户向mysql中添加数据
        # 判断type为专利的数据条是否存在
        if result is None:
            print('mysql的status表中缺失type为%s的数据条，请手动插入' % self.type)
            logging.error('mysql的status表中缺失type为%s的数据条，请手动插入' % self.type)
            # self.conn.close()
            return None
        # 判断开始日期是否存在
        if result[1] == "" or result[1] is None:
            print('mysql的status表中type为%s的数据条缺少关键的开始日期信息，请手动更新' % self.type)
            logging.error('mysql的status表中type为%s的数据条缺少关键的日期信息，请手动更新' % self.type)
            self.conn.close()
            return None
        # 判断结束日期是否存在
        if result[2] == "" or result[2] is None:
            print('未设置初始结束日期信息，已自动设置为昨天')
            logging.info('未设置初始结束日期信息，已自动设置为昨天')
            self.setEndDate(endDate=self.yesterday)
            self.endDate = self.yesterday
        else:
            self.endDate = result[2]
            logging.info("获取的终止日期为 %s" % self.endDate)
        # 判断学科代码是否存在，不存在就默认从code表第一个开始
        if result[0] == "" or result[0] is None:
            code = self.codes[0]
            self.cursor.execute("UPDATE `%s` SET curCode = '%s' WHERE type = '%s'" % (self.table, code, self.type))
            self.conn.commit()
            # conn.close()
            print('未设置初始code信息，已自动设置为', code)
            logging.info('未设置初始code信息，已自动设置为%s' % code)
            return result[1], code
        return result[1], result[0]

    def getNextDateAndCode(self):
        '''
        返回下一个待爬的日期和学科分类
        在爬虫开始的时候先调用getLastDateAndCode
        返回的不是None再调用这个，getNext返回None代表已经爬完了
        :return:
        '''
        lastDate, lastCode = self.getLastDateAndCode()

        oneday = datetime.timedelta(days=1)

        if lastDate > self.endDate:
            logging.info("已经爬完了任务中最后一天的最后一个学科分类，但页面请求和页面解析以及内容存取还在进行中！")
            self.setStatusFinished()
            self.closeConn()
            return None

        index = 0
        # 获取上一个code在当前的日期的记录
        for i in range(len(self.codes)):
            if lastCode == self.codes[i]:
                index = i
                break
        # 某日期的code还没运行完
        if index < len(self.codes) - 1:
            self.markCurrentDateAndCode(lastDate, self.codes[index+1])
            logging.info("获取的下一个日期、学科分类为：%s，%s" % (lastDate, self.codes[index+1]))
            # print("获取的下一个日期、学科分类为：%s，%s" % (lastDate, self.codes[index+1]))
            self.setStatusRunning()
            return lastDate, self.codes[index+1]
        # 所有学科分类的爬完了，爬下一天的
        else:
            # 上一次的日期已经是昨天了，代表爬完（今天的肯定不能爬，因为还没过完)
            if lastDate >= self.endDate:
                logging.info("已经爬完了任务中最后一天的最后一个学科分类，但页面请求和页面解析以及内容存取还在进行中！")
                self.setStatusFinished()
                self.closeConn()
                return None
            # 进入到下一个日期，学科分类置为第一个
            else:
                year = int(lastDate[0:4])
                month = int(lastDate[5:7])
                day = int(lastDate[8:10])
                nextDay = (datetime.date(year, month, day) + oneday).strftime('%Y-%m-%d')
                self.markCurrentDateAndCode(nextDay, self.codes[0])
                logging.debug("获取的下一个日期、学科分类为：%s，%s" % (nextDay, self.codes[0]))
                # print("获取的下一个日期、学科分类为：%s，%s" % (lastDate, self.codes[index+1]))
                self.setStatusRunning()
                return nextDay, self.codes[0]

    def markCurrentDateAndCode(self, date:str, code:str):
        '''
        记录当前正在爬的日期和code至数据库中
        :return:
        '''
        #更新正在爬取的日期和学科分类的sql
        updateSql = "UPDATE `%s` SET curDate = '%s', curCode = '%s' WHERE type = '%s'" % (self.table, date, code, self.type)
        self.cursor.execute(updateSql)
        self.conn.commit()

    def stepIntoNextDate(self, lastDate: str):
        '''
        直接进入到当天的日期
        :param lastDate:
        :return:
        '''
        # year = int(lastDate[0:4])
        # month = int(lastDate[5:7])
        # day = int(lastDate[8:10])
        # oneday = datetime.timedelta(days=1)
        # nextDay = (datetime.date(year, month, day) + oneday).strftime('%Y-%m-%d')
        # 设置上次的日期为当天的最后一个代码，下次获取代码自动会获取到当天的
        self.markCurrentDateAndCode(date=lastDate, code=self.codes[self.codeLen-1])
        logging.warning("%s 无任何专利/论文/成果，已跳过当日" % lastDate)

    def setEndDate(self, endDate):
        '''
        设置默认截止日期为昨天
        :return:
        '''
        self.cursor.execute("UPDATE `%s` SET endDate = '%s' WHERE type = '%s'" % (self.table, endDate, self.type))
        self.conn.commit()

    def setStatusRunning(self):
        '''
        更新数据库中最后一次程序运行时间
        :return:
        '''
        # 更新正在爬取的日期和学科分类的sql
        timeStr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = 'last running:' + timeStr
        updateSql = "UPDATE `%s` SET status = '%s' WHERE type = '%s'" % (
        self.table, status, self.type)
        self.cursor.execute(updateSql)
        self.conn.commit()
        # conn.close()

    def setStatusFinished(self):
        '''
        所有日期和code都已跑完，向数据库中置标记
        :return:
        '''
        # 更新正在爬取的日期和学科分类的sql
        timeStr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = 'finished:' + timeStr
        updateSql = "UPDATE `%s` SET status = '%s' WHERE type = '%s'" % (
        self.table, status, self.type)
        self.cursor.execute(updateSql)
        self.conn.commit()
        # conn.close()

    def getCodeAll(self):
        '''
        从文件中获取所有code信息
        :return:
        '''
        with open(self.srcCodeFile, 'r') as f:
            all = f.read()
            return all.split()

    def closeConn(self):
        '''
        关闭数据库连接
        :return:
        '''
        self.conn.close()


if __name__ == '__main__':
    sm = StatusManager(SpiderTypeEnum.PATENT)
    print(sm.getLastDateAndCode())
    print(sm.getNextDateAndCode())
