#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
分类对应
@author: zyq
'''
from local.shuqi.shuqiLocal import loadCategoryYaml

categoryYaml = loadCategoryYaml()

def getCategoryAndTypeCode(category, type, defaultCategoryCode = 0):
    '''
    根据大小分类名，返回大小分类号和大分类名（因为小分类可能归属于另外一个大分类）
    :param category: 
    :param type: 
    :return: 
    '''

    categoryCode = getClassifyCodeByName(category, default=defaultCategoryCode)['categoryCode']

    mappedCategoryObj = getClassifyCodeByName(type)
    typeCode = 0
    if 0 != mappedCategoryObj['categoryCode']:
        typeCode = mappedCategoryObj['typeCode']
        category = mappedCategoryObj['category']
        categoryCode = mappedCategoryObj['categoryCode']

    return categoryCode, typeCode,category

def getClassifyCodeByName(name, default = 0):
    '''
    根据类型名或标签名返回category的id，已typeCode为准，如果是一级分类categoryCode会跟typeCode一样
    :param default:  默认值，默认0，最好传入已判定值或数据源中分类id
    :return: typeCode: 461
  categoryCode: 452
  category: 奇幻
  url: ''
    '''

    resObj = {
        'typeCode': default,
        'categoryCode': 0,
        'category': '其他',
        'url': ''
    }

    if not name:
        return resObj

    if isinstance(name, str):
        name = name.decode('utf-8')

    if categoryYaml.has_key(name):
        return categoryYaml[name]
    for key in categoryYaml.keys():
        if name in categoryYaml[key]['alias']:
            return categoryYaml[key]
        # if shuqCategory2[name]['id'] and len(shuqCategory2[name]['id']) > 0:
        #     code = int(shuqCategory2[name]['id'])

    return resObj
