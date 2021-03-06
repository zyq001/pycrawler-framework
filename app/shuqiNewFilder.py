#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
追书旗上连载书的更新
@author: zyq
'''
import json
import random
import traceback

import requests
import time

from app.baseCrawler import BaseCrawler
from app.shuqi import start
from dao.connFactory import getDushuConnCsor
# from dao.shuqIdBloom import sourceIdBloom
from dao.sourceIdBloom import srcIdBloom
from util.logHelper import myLogging
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
    myLogging.info('start from %s to %s ', st, end)

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
                    num = start(sqBid, allowUpdate=False)
                    if num and num > 0:
                        srcIdBloom.add('shuqi' + str(sqBid))
                    # start(17043)
                except Exception as e:
                    myLogging.error('shuqi sid: %s , has exception %s', str(sqBid), traceback.format_exc())
                except IOError as e2:
                    myLogging.error('shuqi sid: %s , has exception %s', str(sqBid), traceback.format_exc())


        idx = idx + carry


