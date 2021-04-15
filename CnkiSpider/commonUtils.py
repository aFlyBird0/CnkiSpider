import os
from enum import Enum

class StringUtil:

    @classmethod
    def stringHanlde(cls, s):
        '''
        将非空字符串去首尾空格，空类型设为""
        :param s:
        :return:
        '''
        if s and s is not None:
            s = s.strip()
        else:
            s = ""
        return s

class SpiderTypeEnum(Enum):
    '''
    爬虫类型枚举类，用于状态管理
    '''
    PATENT = "patent"
    JOURNAL = "journal"
    BOSHUO = "boshuo"
    ACHIEVEMENT = "achievement"
    PAPER_AND_ACH = "paperAch"
