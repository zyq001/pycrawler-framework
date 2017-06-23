#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
追书旗上连载书的更新
@author: zyq
'''
import json
import random

import requests
import time

from app.baseCrawler import BaseCrawler
from app.shuqi import start
from dao.connFactory import getDushuConnCsor
# from dao.shuqIdBloom import sourceIdBloom
from dao.sourceIdBloom import srcIdBloom
from util.timeHelper import getToday

class ShuqiFilder(BaseCrawler):

    def __init__(self):
        self.st = 10000
        self.end = 7000000

    def init(self, data = None):
        print 'shuqi filder init'
        if data:
            if data.has_key('st'):
                self.st = data['st']
            if data.has_key('end'):
                self.end = data['end']

    def crawl(self):
        updateFromMysql(self.st, self.end)

    def output(self):
        print 'shuqi filder output'

def updateFromMysql(st = 10000, end = 7000000):
    '''
        永远运行，从数据库中查询出于连载状态的小说，进行更新
    '''

    idx = st
    carry = 10000

    while idx < end:
        # seq = range(5000, 6000)
        seq = range(idx, idx + carry)

        random.shuffle(seq)
        #
        for sqBid in seq:
            # print sqBid
            # if sqBid in nullIdSet:
            #     continue
            if not srcIdBloom.contains('shuqi' + str(sqBid)) :
                try:
                    start(sqBid, allowUpdate=False)
                    # start(17043)
                except Exception as e:
                    print sqBid, ':  ', e
                except IOError as e2:
                    print sqBid, ':  ', e2

                srcIdBloom.add('shuqi' + str(sqBid))

        idx = idx + carry