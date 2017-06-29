#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
日志设置
@author: zyq
'''

import logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.INFO)

myLogging = logging