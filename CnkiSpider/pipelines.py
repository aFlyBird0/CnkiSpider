# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from CnkiSpider.file_util import FileUtil
from CnkiSpider.commonUtils import SpiderTypeEnum
import csv


class CnkispiderPipeline:
    def process_item(self, item, spider):
        if spider.name == 'patent':
            year = item['year']
            resultPath = FileUtil.mkResultYearTypeDir(year, item['type'])
            resultFilename = resultPath + item['naviCode'] + '.csv'
            FileUtil.write_header(resultFilename, item.keys())
            item = self.removeLineFeed(item)
            with open(resultFilename, 'a', encoding='utf-8', newline='') as f:
                csvWriter = csv.DictWriter(f, item.keys())
                csvWriter.writerow(item)
        elif spider.name == 'paperAch':
            year = item['year']
            # 不同类型的根据type字段直接新建对应的文件夹
            resultPath = FileUtil.mkResultYearTypeDir(year, item['type'])
            resultFilename = resultPath + item['naviCode'] + '.csv'
            FileUtil.write_header(resultFilename, item.keys())
            item = self.removeLineFeed(item)
            with open(resultFilename, 'a', encoding='utf-8', newline='') as f:
                csvWriter = csv.DictWriter(f, item.keys())
                csvWriter.writerow(item)
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
