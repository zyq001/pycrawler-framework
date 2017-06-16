#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
from app.baseCrawler import BaseCrawler
from app.shuqi import start


class ShuqiCrawler(BaseCrawler):

    def __init__(self, sid):
        self.sid = sid

    def init(self):
        print 'shuqi init'

    def crawl(self):
        print 'shuqi init'
        start(self.sid)

    def output(self):
        print 'shuqi output'