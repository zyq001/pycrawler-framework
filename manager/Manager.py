#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
管理类，进程池调度等
@author: zyq
'''
from manager.Task import Task


class Manager():
    def __init__(self):
        self.crawlers = dict()

    def addCrawler(self, name, crawler):
        self.crawlers[name] = crawler

    def startAll(self):
        for crawler in self.crawlers:
            task = Task(crawler)
            task.start()

    def getCrawlerByName(self, name):
        if self.crawlers.has_key(name):
            return self.crawlers[name]
        return None

# 单例
crawlManager = Manager()
