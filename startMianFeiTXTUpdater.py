#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
import time

from app.mianfeiTXTUpdater import mianfeiTxtUpdateFromMysql
from local.hotConfigHelper import getHotConfigDict
from util.logHelper import myLogging

if __name__ == '__main__':
    while 1:
        myLogging.info('begin mianfeiTXT updater')
        mianfeiTxtUpdateFromMysql()
        sleepTime = getHotConfigDict()['mianFeiTXTUpdater']['updateSleep']
        myLogging.info(' done one loop, now sleep '+ str(sleepTime) + ' secs')
        time.sleep(int(sleepTime))