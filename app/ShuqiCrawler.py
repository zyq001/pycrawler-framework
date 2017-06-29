#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
from app.baseCrawler import BaseCrawler
from app.shuqi import start
from exception.InputException import InputException
from util.logHelper import myLogging


class ShuqiCrawler(BaseCrawler):

    # def __init__(self):
    #     super(self)
        # self.sid = sid

    def init(self, data = None):
        if not data or not isinstance(data, dict):
            raise InputException("requried dict data with fields: sid")
        if not data.has_key('id'):
            raise InputException("requried field 'id' in data")

        self.sid = data['id']
        self.data = data

    def crawl(self):
        myLogging.info('shuqi init')

        start(self.sid)

    def output(self):
        myLogging.info('shuqi output')