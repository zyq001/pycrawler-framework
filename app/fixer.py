#!/usr/bin/python
# -*- coding: UTF-8 -*-
import hashlib
import json
import traceback

import requests

from Config import ossBaseUrl
# from app.ZssqSearcher import searchAndCrawl
from app.shuqi import getContentByUrl
from dao.aliyunOss import upload2Bucket, bucket, uploadJson2Bucket
from dao.connFactory import getDushuConnCsor
from dao.dushuQuanBenService import getQuanBenAllBookIds
from dao.dushuService import updateContentById, getCapIdsByBookId, delCapById
from parse.easouParser import getAndParse
from util.logHelper import myLogging
from util.networkHelper import getERAConn


def handleCapUpload(cap):
    cid = cap[0]
    capUrl = cap[2]
    bookId = cap[5]
    unclearContent = cap[4]
    capObj = dict()
    capObj['id'] = cap[0]
    capObj['title'] = cap[1]
    capObj['rawUrl'] = cap[2]
    capObj['source'] = cap[3]
    capObj['content'] = cap[4]
    capObj['bookId'] = cap[5]
    capObj['idx'] = cap[6]
    capObj['digest'] = cap[7]
    capObj['size'] = cap[8]
    capObj['bookUUID'] = cap[9]
    content = unclearContent
    if unclearContent and not (u'        言情小说_打造最新原创' in unclearContent or unclearContent == 'None'):
        uploadJson2Bucket(str(cid) + '.json', json.dumps(capObj))
    else:
        try:
            if not capUrl or len(capUrl) < 1:
                print cid, 'no url, bookId : ', bookId
            else:
                if 'shuqireader' in capUrl:
                    content = getContentByUrl(capUrl)
                    # updateContentById(cid, content)
                else:
                    content, host = getAndParse(capUrl)
                    if not content:
                        print cid, ' getAndparse content failed, bookId : ', bookId
                        # continue
                        # updateContentById(cid, content)
                        # cap[4] = content
            capObj['content'] = content

            upload2Bucket(str(cid) + '.json', json.dumps(capObj))
        except Exception as e:
            print 'cid ', cid, 'error: ', e
        except ValueError as er:
            print 'cid ', cid, 'error: ', er

def updateCapDigest():


    conn2,csor2 = getDushuConnCsor()

    for i in range(1056363, 1722907):
        try:
            capObj = json.loads(bucket.get_object(str(i) + '.json').read())
        except Exception as e:
            print i, e
            continue

    # for cap in caps:
        cid = capObj['id']
        print cid
        bookDigest = capObj['bookUUID']
        capTitle = capObj['title']
        idx = capObj['idx']

        m2 = hashlib.md5()
        forDigest = bookDigest + capTitle + u'#' + str(idx)
        m2.update(forDigest.encode('utf-8'))
        digest2 = m2.hexdigest()

        try:
            csor2.execute("update cn_dushu_acticle set digest = %s where id = %s",
                          (digest2, cid))
            conn2.commit()
        except Exception as e:
            print cid, e

    csor2.close()
    conn2.close()

def uploadCapByCid(capId):

    conn2,csor2 = getDushuConnCsor()

    print capId

    offset = 200

    try:
        csor2.execute("select * from cn_dushu_acticle where id = " + str(capId) )
        conn2.commit()
    except Exception as e:
        #     # 发生错误时回滚
        print 'mysql ex: ', e
        return

    results = csor2.fetchall()
    for cap in results:
        handleCapUpload(cap)

    csor2.close()
    conn2.close()

def updateCapFromTo(f, t):

    conn2,csor2 = getDushuConnCsor()

    print 'from', str(f), ' to ', str(t)

    offset = 100

    begin = f
    end = begin + offset
    while end <= t:
        # sql = "select id, rawUrl,bookId,content from cn_dushu_acticle where id >= %d and id < %d" % (begin, end)
        try:
            csor2.execute("select id, rawUrl,bookId,content from cn_dushu_acticle where id >= %d and id < %d",
                          (begin, end))
            conn2.commit()
        except Exception as e:
            #     # 发生错误时回滚
            print 'mysql ex: ', e

        begin = begin + offset
        end = end + offset

        results = csor2.fetchall()
        for cap in results:
            cid = cap[0]
            capUrl = cap[1]
            bookId = cap[2]
            unclearContent = cap[3]
            if not (u'        言情小说_打造最新原创' in unclearContent or unclearContent == 'None'):
                continue
            try:
                if not capUrl or len(capUrl) < 1:
                    print 'no url, bookId : ', bookId
                if 'shuqireader' in capUrl:
                    content = getContentByUrl(capUrl)
                    # updateContentById(cid, content)
                else:
                    content, host = getAndParse(capUrl)
                    if not content:
                        continue
                updateContentById(cid, content)
            except Exception as e:
                print 'cid ', cid, 'error: ', e
            except ValueError as er:
                print 'cid ', cid, 'error: ', er

    csor2.close()
    conn2.close()


def uploadCapFromTo(f, t):


    csor3,conn3 = getERAConn()

    if t < f:
        print 'input end > start'
        return
    print 'from', str(f), ' to ',str(t)

    offset = 200
    begin = f
    end = begin + offset
    if end > t:
        end = t
    while end <= t:
        # sql = "select id, rawUrl,bookId,content from cn_dushu_acticle where id >= %d and id < %d" % (begin, end)
        try:
            csor3.execute("select * from cn_dushu_acticle where bookId = 47621 and id >= %d and id < %d" % (begin, end))
            conn3.commit()
        except Exception as e:
            #     # 发生错误时回滚
            print 'mysql ex: ', e
            continue

        begin = begin + offset
        end = end + offset

        results = csor3.fetchall()
        for cap in results:
            handleCapUpload(cap)

# def crawlBySearchHistory():
#     baseUrl = 'http://%s/log/_search'  % SEARCHHOST
#     searchInput = '''
#     {
# "size":0,
# "query": {
#     "range" : {
#         "page" : {
#             "gte" : 1
#         }
#     }
#  },
#  "aggs":{
#  "hist": {
#       "terms": {
#         "field": "word.raw",
#         "size": 1000,
#         "order": {
#           "_count": "desc"
#         }
#       }
#     }
#  }
#  }
#     '''
#     r = requests.post(baseUrl, data = searchInput)
#     resObj = json.loads(r.text)
#     for wordObj in resObj['aggregations']['hist']['buckets']:
#         word = wordObj['key']
#         searchAndCrawl(word)

def newLineFixer():

    # quanBenObjs = getQuanBenAllBookIds()
    quanBenObjs = [{'id':2137876}]
    fixNewLineByBookObjs( quanBenObjs)

    # zssqObjs = getZssqAllBookObjs()
    # fixNewLineByBookObjs( zssqObjs)


def fixNewLineByBookObjs( quanBenObjs):

    from parse.contentHelper import textClean
    for quanBenObj in quanBenObjs:
        bookId = quanBenObj['id']
        chapIds = getCapIdsByBookId(bookId)
        for chapId in chapIds:
            try:
                url = ossBaseUrl + str(chapId) + '.json'
                r = requests.get(url)

                obj = json.loads(r.text)

                if not obj or not obj.has_key('content'):
                    delCapById(chapId)
                    myLogging.info('chap id %s, has no oss obj, delete', chapId)
                    continue

                content = textClean(obj['content'])
                obj['content'] = content

                uploadJson2Bucket(str(chapId) + '.json', json.dumps(obj))
                myLogging.info('succ cid %s', chapId)
            except Exception as e:
                myLogging.error('chap id %s, with exception: %s', chapId, traceback.format_exc())
if __name__ == '__main__':
    newLineFixer()