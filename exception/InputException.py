#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
输入异常
@author: zyq
'''


class InputException(Exception):
    def __init__(self, msg):
        # super(self)
        self.message = msg