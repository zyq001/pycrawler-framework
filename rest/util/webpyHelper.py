#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
封装web.py的一些功能
@author: zyq
'''
import json


def getParams(web, **kwargs):
    params = dict()
    paramsInput = web.input(**kwargs)
    params.update(paramsInput)

    inputData = web.data()
    if '' != inputData:
        inputJson = json.loads(inputData)
        params.update(inputJson)
    return params