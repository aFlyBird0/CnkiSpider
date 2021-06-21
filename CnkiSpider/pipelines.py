# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from CnkiSpider.file_util import FileUtil
from CnkiSpider.commonUtils import SpiderTypeEnum
from CnkiSpider.items import *
import csv


class CnkispiderPipeline:
    def process_item(self, item, spider):
        if spider.name == 'patent':
            if isinstance(item, PatentContentItem):
                year = item['year']
                resultPath = FileUtil.mkResultYearTypeDir(year, item['type'])
                # 每个细分学科分类存成一个文件
                # resultFilename = resultPath + item['naviCode'] + '.csv'
                # 每个大学科分类存成一个文件
                resultFilename = resultPath + item['naviCode'][0] + '.csv'
                FileUtil.write_header(resultFilename, item.keys())
                item = self.removeLineFeed(item)
                FileUtil.saveItem(resultFilename=resultFilename, item=item)
            elif isinstance(item, ErrorUrlItem):
                # self.markLinkError(item['url'], SpiderTypeEnum.PATENT.value)
                self.easyMarkErrorItem(item)

        elif spider.name == 'paperAch':
            if isinstance(item, PatentContentItem) or isinstance(item, JournalContentItem)\
                    or isinstance(item, BoshuoContentItem) or isinstance(item, AchContentItem):
                year = item['year']
                # 不同类型的根据type字段直接新建对应的文件夹
                resultPath = FileUtil.mkResultYearTypeDir(year, item['type'])
                # 每个细分学科分类存成一个文件
                # resultFilename = resultPath + item['naviCode'] + '.csv'
                # 每个大学科分类存成一个文件
                resultFilename = resultPath + item['naviCode'][0] + '.csv'
                FileUtil.write_header(resultFilename, item.keys())
                item = self.removeLineFeed(item)
                FileUtil.saveItem(resultFilename=resultFilename, item=item)
            elif isinstance(item, ErrorUrlItem):
                # self.markLinkError(item['url'], SpiderTypeEnum.PATENT.value)
                self.easyMarkErrorItem(item)
        return item

    def removeLineFeed(self, item):
        '''
        消除item的换行
        :param item:
        :return:
        '''
        for key in item:
            if item[key]:
                item[key] = item[key].replace('\n', '').replace('\r', ' ')
        return item

    def markLinkError(self, url, type):
        with open(FileUtil.errorLinkDir + type + 'Error.txt', 'a', encoding='utf-8') as file:
            file.write(url + '\n')

    def easyMarkErrorItem(self, item: ErrorUrlItem):
        '''
        简单的记录错误，先都存到同一个文件中
        :param item:
        :return:
        '''
        resultPath = FileUtil.errorDir()
        resultFilename = resultPath + 'allErrors.csv'
        FileUtil.write_header(resultFilename, item.keys())
        item = self.removeLineFeed(item)
        with open(resultFilename, 'a', encoding='utf-8', newline='') as f:
            csvWriter = csv.DictWriter(f, item.keys())
            csvWriter.writerow(item)
