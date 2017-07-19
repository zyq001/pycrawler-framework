#!/usr/bin/python
# -*- coding: UTF-8 -*-
from util.yamlHelper import loadYaml

def loadCategoryYaml():
    return loadYaml('local/category.yaml')

def loadShuQC():
    return loadYaml('local/shuqi/shuqCategory.yaml')

def loadShuQSeqC():
    return loadYaml('local/shuqi/shuqCategorySeq.yaml')
