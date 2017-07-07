#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
import time

from app.QuanbenUpdater import updateFromMysql
from local.hotConfigHelper import getHotConfigDict
from util.logHelper import myLogging

if __name__ == '__main__':
    while 1:
        myLogging.info('begin quanben updater')
        updateFromMysql()
        sleepTime = getHotConfigDict()['quanBenUpdater']['updateSleep']
        myLogging.info(' done one loop, now sleep '+ str(sleepTime) + ' secs')
        time.sleep(int(sleepTime))