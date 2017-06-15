#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
管理类，进程池调度等
@author: zyq
'''


class Manager():
    def __init__(self):
        self.crawlTasks = list()

    def addCrawler(self, crawler, crawler_count=1, output_count=1):
        task = dict()
        task['crawler'] = crawler
        task['crawler_count'] = crawler_count
        task['output_count'] = output_count
        self.crawlTasks.append(task)

    def start(self):
        for task in self.crawlTasks:
            crawler = task['crawler']
            crawler_count = task['crawler_count']
            output_count = task['output_count']

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
