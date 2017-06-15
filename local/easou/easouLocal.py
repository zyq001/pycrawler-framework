#!/usr/bin/python
# -*- coding: UTF-8 -*-
from util.yamlHelper import loadYaml


def loadRules():
    # try:
    #     conf = s=yaml.load(file('rules.yaml'))
    # except Exception as e:
    #     print e
    #     return None
    return loadYaml('local/easou/rules.yaml')


def loadIgnores():
    # try:
    #     conf = s=yaml.load(file('ignore.yaml'))
    # except Exception as e:
    #     print e
    #     return None
    return loadYaml('local/easou/ignore.yaml')