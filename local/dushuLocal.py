#!/usr/bin/python
# -*- coding: UTF-8 -*-
from util.yamlHelper import loadYaml


def loadCategory():
    return loadYaml('local/category.yaml')


def loadCrawledBook():

    from pybloom import BloomFilter
    f = BloomFilter(capacity=10000000, error_rate=0.001)
    return f