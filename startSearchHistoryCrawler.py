#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
import time

from app.SearchHistoryCrawler import crawlByDailySearchHistory
from app.shuqiUpdater import updateFromMysql
from local.hotConfigHelper import getHotConfigDict
from util.logHelper import myLogging
# import logging
# logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.INFO)
if __name__ == '__main__':
    timeStart = int(time.time() * 1000) - 24 * 3600 * 1000
    while 1:
        myLogging.info('begin searchHistoryCrawler')
        crawlByDailySearchHistory(timeStart)
        timeStart = int(time.time() * 1000)
        sleepTime = getHotConfigDict()['searchHistoryCrawler']['updateSleep']
        myLogging.info(' done one loop, now sleep '+ str(sleepTime) + ' secs')
        time.sleep(int(sleepTime))