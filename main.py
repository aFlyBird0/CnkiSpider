from scrapy import cmdline

if __name__ == '__main__':
    # cmdline.execute("scrapy crawl patent".split())
    # cmdline.execute("scrapy crawl patent -s JOBDIR=jobs/patent-1".split())
    cmdline.execute("scrapy crawl paperAch".split())