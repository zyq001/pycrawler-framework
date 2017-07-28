#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
import json
import sys

from Config import MianFeiTXTBookBaseUrl, MianFeiTXTChannelBaseUrl
from app.mianfeiTXTCrawler import handleByMTID
from app.mianfeiTXTNewFilder import findByIdRange

# secondCategoryId=101&thirdCategoryId=1011&filterId=0&sortId=1&pageSize=15&pageNum=1
from util.networkHelper import getContentWithUA
from util.signHelper import paramMap


def fromCategoryId(categoryId):
    url = MianFeiTXTChannelBaseUrl + '?' + paramMap().mianfeiTXT().put('secondCategoryId', 101)\
        .put('thirdCategoryId',0).put('filterId', 0).put('sortId',1).put('pageSize', 2000).put('pageNum',1)\
        .mianfeiTXTSign().toUrl()

    baseInfoContent = getContentWithUA(url)
    if not baseInfoContent:
        baseInfoContent = getContentWithUA(url)
    baseObj = json.loads(baseInfoContent)
    for bookObj in baseObj['data']['books']:
        mid = bookObj['id']
        handleByMTID(mid)

if __name__ == '__main__':

    # handleByMTID(15360)
    # fromCategoryId(101)
    st = 0
    end = 500000
    if len(sys.argv) > 1:
        st = int(sys.argv[1])
        end = int(sys.argv[2])

    findByIdRange(st, end)