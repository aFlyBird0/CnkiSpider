import csv
import os
import random
import string
import sys
import logging

class PackUtil:
    '''
    打包工具，做一个文件路径转换
    '''
    @classmethod
    def resource_path(cls, relative_path: str):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

class FileUtil:
    '''
    文件工具类
    '''


    # 如下方式，运行时，不打包则会生成在项目目录，打包会生成在exe内部(运行结束消失）
    # targetDir = PackUtil.resource_path("./target/")
    # resultDir = PackUtil.resource_path("./result/")
    # htmlDir = PackUtil.resource_path("./html/")
    # errorDir = PackUtil.resource_path("./error/")
    # logDir = PackUtil.resource_path("./log/")
    #
    # errorLinkDir = PackUtil.resource_path("./error/link/")
    # errorOverflowDir = PackUtil.resource_path("./error/overflow/")
    # errorDayDir = PackUtil.resource_path("./error/day/")
    # errorPageDir = PackUtil.resource_path("./error/page/")

    # 如下方式，运行时，不打包则会生成在项目目录，打包会生成在exe同级目录
    targetDir = "./target/"
    resultDir = "./result/"
    htmlDir = "./html/"
    errorDir = "./error/"
    logDir = "./log/"

    errorLinkDir = "./error/link/"
    errorOverflowDir = "./error/overflow/"
    errorDayDir = "./error/day/"
    errorPageDir = "./error/page/"

    # @classmethod
    # def write_header(cls, filename, header):
    #     '''
    #             (已废弃）不存在文件则创建文件，不存在header则写入hearder，创建header
    #             :return:
    #             '''
    #     # newline的作用是防止每次插入都有空行
    #     with open(filename, "a+", newline='', encoding='utf-8') as csvfile:
    #         writer = csv.DictWriter(csvfile, header)
    #         # 以读的方式打开csv 用csv.reader方式判断是否存在标题。
    #         with open(filename, "r", newline="", encoding='utf-8') as f:
    #             reader = csv.reader(f)
    #             if not [row for row in reader]:
    #                 writer.writeheader()

    @classmethod
    def write_header(cls, filename, header):
        '''
        不存在文件则创建文件并写入header
        没有上一个函数严谨，但可以避免文件读取写入冲突
        :return:
        '''
        # newline的作用是防止每次插入都有空行
        if not os.path.exists(filename):
            with open(filename, "a+", newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, header)
                writer.writeheader()

    @classmethod
    def saveItem(cls, resultFilename, item):
        with open(resultFilename, 'a', encoding='utf-8', newline='') as f:
            csvWriter = csv.DictWriter(f, item.keys())
            csvWriter.writerow(item)

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
        cls.mkDirsIfNotExist(cls.logDir)
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
    def saveHtml(cls, year, response, type:str, url, title):
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

    @classmethod
    def markFinishOnce(cls):
        '''
        标记成功运行，连续标记两次证明程序运行完成
        :return:
        '''
        filenameOne = "1.txt"
        filenameTwo = "2.txt"
        if os.path.exists(filenameTwo):
            logging.info("已经运行两次了")
        elif os.path.exists(filenameOne):
            logging.info("第二次运行完成")
            with open(filenameTwo, "w", encoding="utf-8") as f:
                f.write("第二次运行完成，所有任务完成，请将整个文件夹返还，谢谢！\n")
        else:
            logging.info("第一次运行完成")
            with open(filenameOne, "w", encoding="utf-8") as f:
                f.write("第一次运行完成，请再次运行exe文件，并不要删除此文件，等待2.txt生成\n")
    @classmethod
    def IfFinishTask(cls):
        '''
        本次分发的任务是否完成
        :return:
        '''
        filenameOne = "1.txt"
        filenameTwo = "2.txt"
        return os.path.exists(filenameTwo)
