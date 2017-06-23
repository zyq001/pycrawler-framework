#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
import traceback

from app.qichacha import searchAndCrawlByName

if __name__ == '__main__':

    while 1:
        try:
            try:
                searchAndCrawlByName("noName")
            except Exception as e:
                print traceback.format_exc()
        except Exception as ge:
            print traceback.format_exc()
