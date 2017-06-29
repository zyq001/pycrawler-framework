#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
加载维护热更新配置文件
@author: zyq
'''
from util.yamlHelper import loadYaml


def getHotConfigDict():
    return loadYaml('hotConfig.yaml')