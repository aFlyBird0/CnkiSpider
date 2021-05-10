import os

class ItemAnalyse:

    resultPath = "./result"

    @classmethod
    def getAllItemNums(cls):
        # result文件夹层级如下：./result/年份/类型
        sum = 0
        for yearDir in os.listdir(cls.resultPath):
            for typeDir in os.listdir(cls.resultPath + '/' + yearDir):
                sum += cls.getPathItemNums(cls.resultPath + '/' + yearDir + '/' + typeDir)
        return sum

    @classmethod
    def getPathItemNums(cls, path:str):
        sum = 0
        for file in os.listdir(path):
            sum += cls.getOneFileItemNums(path.rstrip('/') + '/' + file)
        return sum


    @classmethod
    def getOneFileItemNums(cls, pathFilename: str):
        with open(pathFilename, mode="r", encoding='utf-8') as f:
            lines = f.readlines()
            return len(lines) - 1

    @classmethod
    def getCodeSrcNewList(cls, filename):
        with open(filename, mode="r", encoding='utf-8') as f:
            src = f.readline()
            return src.split(',')

    @classmethod
    def writeNewCodeSrc(cls, filename, codeSrcList):
        with open(filename, mode="a", encoding='utf-8') as f:
            for code in codeSrcList:
                f.write(code + "\n")

if __name__ == '__main__':
    # num = ItemAnalyse.getPathItemNums("./result/2020/boshuo")
    # print(num)
    # codeSrcList = ItemAnalyse.getCodeSrcNewList("./dataSrc/codeSrc.txt")
    # print(len(codeSrcList))
    # ItemAnalyse.writeNewCodeSrc("./dataSrc/codeNewest.txt", codeSrcList)

    num = ItemAnalyse.getAllItemNums()
    print(num)