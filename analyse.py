import os

class ItemAnalyse:
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

if __name__ == '__main__':
    num = ItemAnalyse.getPathItemNums("./result/2020/patent")
    print(num)