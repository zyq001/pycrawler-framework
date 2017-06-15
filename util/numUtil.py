#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''


def str2intNoDot(str):
    '''atoi, 忽略小数点'''
    index = str.find('.')
    if index > 0:
        return int(str[0:index])
    else:
        return int(str)