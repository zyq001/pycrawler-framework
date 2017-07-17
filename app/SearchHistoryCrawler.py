#!/usr/bin/python
# -*- coding: UTF-8 -*-
import hashlib
import json

import requests
import time

from Config import SEARCHHOST
from app.ZhuiShuShenQiCrawler import searchAndCrawl
from app.shuqi import getContentByUrl
from dao.aliyunOss import upload2Bucket, bucket
from dao.connFactory import getDushuConnCsor
from dao.dushuService import updateContentById
from parse.easouParser import getAndParse
from util.networkHelper import getERAConn


def crawlByDailySearchHistory(timeStart = None):
    baseUrl = 'http://%s/log/_search'  % SEARCHHOST
    if not timeStart:
        timeStart = int(time.time() * 1000) - 24 * 3600 * 1000
    searchInput = '''
    {
"size":0,
"query": {
	"bool":{
		"must":[{
		    "range" : {
		        "page" : {
		            "gte" : 1
		        }
	    	}
	    },
	    {
		    "range" : {
		        "timestamp" : {
		            "gte" : %s
		        }
		    }
		   }
    	]
    }
 },
 "aggs":{
 "hist": {
      "terms": {
        "field": "word.raw",
        "size": 100,
        "order": {
          "_count": "desc"
        }
      }
    }
 }
 }
    ''' % (str(timeStart))
    r = requests.post(baseUrl, data = searchInput)
    resObj = json.loads(r.text)
    for wordObj in resObj['aggregations']['hist']['buckets']:
        word = wordObj['key']
        searchAndCrawl(word)

if __name__ == '__main__':
    crawlByDailySearchHistory()