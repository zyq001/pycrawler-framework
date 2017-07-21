#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
import time

import sys

from app.searchSuggest import indexBookSuggest
from app.zssqUpdater import updateFromMysql
from local.hotConfigHelper import getHotConfigDict
from util.logHelper import myLogging
# import logging
# logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.INFO)
if __name__ == '__main__':

    st = 200000

    if len(sys.argv) > 1:
        st = int(sys.argv[1])

    indexBookSuggest(st)