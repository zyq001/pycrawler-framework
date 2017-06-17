#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
from app.baseCrawler import BaseCrawler
from app.shuqi import start
from exception.InputException import InputException


class ShuqiCrawler(BaseCrawler):

    # def __init__(self):
    #     super(self)
        # self.sid = sid

    def init(self, data = None):
        if not data or not isinstance(data, dict):
            raise InputException("requried dict data with fields: sid")
        if not data.has_key('sid'):
            raise InputException("requried field 'sid' in data")

        self.sid = data['sid']

    def crawl(self):
        print 'shuqi init'
        start(self.sid)

    def output(self):
        print 'shuqi output'