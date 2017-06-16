#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
任务类，@TODO 任务的起停
@author: zyq
'''


class Task():
    def __init__(self, cralwler, crawler_count=1, output_count=1):
        self.crawler = cralwler
        self.crawler_count = crawler_count
        self.output_count = output_count

    def start(self):
        crawler = self.crawler['crawler']
        crawler_count = self.crawler['crawler_count']
        output_count = self.crawler['output_count']

        crawler.init()

        #           @TODO 按照配置的爬虫和入库进程数起对应的进程
        if 1 == crawler_count:
            crawler.crawl()
        else:
            raise NotImplementedError

        if 1 == output_count:
            crawler.output()
        else:
            raise NotImplementedError
