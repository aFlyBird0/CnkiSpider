import csv
import os
import random
import string

class FileUtil:
    '''
    文件工具类
    '''

    targetDir = "./target"
    resultDir = "./result"
    htmlDir = "./html"
    errorDir = "./error"

    errorLinkDir = "./error/link/"
    errorOverflowDir = "./error/overflow/"
    errorDayDir = "./error/day/"
    errorPageDir = "./error/page/"

    @classmethod
    def write_header(cls, filename, header):
        '''
                不存在文件则创建文件，不存在header则写入hearder，创建header
                :return:
                '''
        # newline的作用是防止每次插入都有空行
        with open(filename, "a+", newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, header)
            # 以读的方式打开csv 用csv.reader方式判断是否存在标题。
            with open(filename, "r", newline="", encoding='utf-8') as f:
                reader = csv.reader(f)
                if not [row for row in reader]:
                    writer.writeheader()
    @classmethod
    def remove_reduntant_header_one_file(cls, dir_path: str, filename: str):
        '''
        删除某个文件多余的header
        :param filename:
        :return:
        '''
        num = 0
        actual_filename = dir_path + '/' + filename
        with open(actual_filename, 'r', encoding='utf-8') as fin:
            # 处理好的文件换个文件夹，放在 '原文件夹名_handled' 里面
            output_filename = dir_path + '_handled/' + filename
            with open(output_filename, 'a+', encoding='utf-8', newline='') as fout:
                header = fin.readline() #读取第一行，第一行的标题要保留
                fout.write(header)
                for line in fin.readlines():
                    # 忽略以后的标题行
                    if line[0:7] != 'authors' and line[0:3] != 'DOI':
                        fout.write(line)
                        num += 1
        return num

    @classmethod
    def remove_reduntant_header_one_dir(cls, dir_path: str):
        '''
        删除某个文件夹下所有文件的多余header
        :return:
        '''
        for filename in os.listdir(dir_path):
            cls.remove_reduntant_header_one_file(dir_path, filename)

    @classmethod
    def mkResultYearTypeDir(cls, year: str, type: str):
        '''
        创建每一年每个文章种类的文件夹
        :param year:
        :param type:专利、博硕、期刊, 成果，值为paten, boshuo, journal,achievement
        :return:
        '''
        resultDir = 'result/'
        yearTypeDir = resultDir + year + '/' + type + '/'
        if not os.path.exists(yearTypeDir):
            os.makedirs(yearTypeDir)
        return yearTypeDir

    @classmethod
    def mkDirsIfNotExist(cls, dirsName):
        if not os.path.exists(dirsName):
            os.makedirs(dirsName)

    @classmethod
    def initOutputDir(cls):
        '''
        初始化输出文件夹
        :return:
        '''
        cls.mkDirsIfNotExist(cls.targetDir)
        cls.mkDirsIfNotExist(cls.resultDir)
        cls.mkDirsIfNotExist(cls.htmlDir)
        cls.mkDirsIfNotExist(cls.errorDir)
        cls.mkErrorLinkDirs()
        cls.mkErrorOverflowDirs()
        cls.mkErrorDayDirs()
        cls.mkErrorPageDirs()


    @classmethod
    def mkErrorLinkDirs(cls):
        '''
        出错链接文件夹,按item类型分类，期刊，博硕，成果，专利
        :param type:
        :return:
        '''
        cls.mkDirsIfNotExist(cls.errorLinkDir)

    @classmethod
    def mkErrorOverflowDirs(cls):
        cls.mkDirsIfNotExist(cls.errorOverflowDir)

    @classmethod
    def mkErrorDayDirs(cls):
        cls.mkDirsIfNotExist(cls.errorDayDir)

    @classmethod
    def mkErrorPageDirs(cls):
        cls.mkDirsIfNotExist(cls.errorPageDir)

    @classmethod
    def saveHtml(cls, year, response, type, url, title):
        '''
        存放html文件
        :param response:
        :param type:
        :param url:
        :param title:
        :return:
        '''
        # 根据年份和类型存储html源文件，每个网页单独存储一个文件
        filepath = './html/' + year + '/' + type + '/'
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        # 按标题命名, 加个随机字符防止文件被覆盖，因为存在同名专利
        ranStr = ''.join(random.sample(string.ascii_letters + string.digits, 3))
        htmlFileName = filepath + cls.handleFilename(title) + '_' + ranStr + '.html'
        with open(htmlFileName, 'w', encoding='utf-8') as f:
            f.write(response.text)

    @classmethod
    def handleFilename(cls, filename):
        '''
        windows的文件名中不能含有一些特殊字符，所以要处理一下文件名
        :param filename:
        :return:
        '''
        sets = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in filename:
            if char in sets:
                filename = filename.replace(char, '')
        return filename.replace('\n', '').replace('\r', ' ')
