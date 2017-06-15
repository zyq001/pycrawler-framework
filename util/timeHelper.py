#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
import time


def getYesteday():
    return time.strftime('%Y%m%d', time.localtime(time.time() - 24 * 3600))


def getToday():
    return time.strftime('%Y%m%d', time.localtime(time.time()))