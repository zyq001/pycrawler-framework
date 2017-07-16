#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
import sys

# from app.mianfeiTXTNewFilder import findByIdRange
import time

from app.shuqi import start
from app.shuqiNewFilder import updateFromMysql
from local.hotConfigHelper import getHotConfigDict
from util.logHelper import myLogging

if __name__ == '__main__':
    # start('10650', allowUpdate=False)

    st = 50000
    end = 500000
    if len(sys.argv) > 1:
        st = int(sys.argv[1])
        end = int(sys.argv[2])

    updateFromMysql()
    sleepTime = getHotConfigDict()['shuqiNewFinder']['updateSleep']
    myLogging.info(' done one loop, now sleep ' + str(sleepTime) + ' secs')
    time.sleep(int(sleepTime))