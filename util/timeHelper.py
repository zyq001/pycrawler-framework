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

def getFormatedTime(format):
    '''
    到秒级的时间 例如 20170701175131
    :return: str
    '''
    return time.strftime(format, time.localtime())

def getFormatedTimeSec():
    '''
    到秒级的时间 例如 20170701175131
    :return: str
    '''
    format = '%Y%m%d%H%M%S'
    return getFormatedTime(format)
