#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
import time

from app.shuqiUpdater import updateFromMysql
from local.hotConfigHelper import getHotConfigDict

if __name__ == '__main__':
    while 1:
        print 'begin shuqi updater'
        updateFromMysql()
        sleepTime = getHotConfigDict()['shuqiUpdater']['updateSleep']
        print ' done one loop, now sleep ', str(sleepTime) + ' secs'
        time.sleep(int(sleepTime))