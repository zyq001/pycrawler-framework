#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
dao实现类，实现对entity的增删改查
 zyq

'''
import json
import random
import re

import time

from dao.aliyunOss import upload2Bucket
from dao.connFactory import getDushuConnCsor
from parse.easouParser import getAndParse
from util.pyBloomHelper import getBloom, dumpBloomToFile

db_dushu = 'cn_dushu_book'
db_acticle = 'cn_dushu_acticle'


def updateBookTypeByRawUrl(type, rawUrl):
    conn, csor = getDushuConnCsor()
    try:
        csor.execute("update " + db_dushu + " set bookType = %s where rawUrl = %s", (type, rawUrl,))
        conn.commit()
    except Exception as e:
        print 'update bookType exception: ',e


def handleWebsiteNoise(begin, end):

    conn2,csor2 = getDushuConnCsor()

    sql = 'select id,content from cn_dushu_acticle where bookId = 960 and id > ' + str(begin) + ' and id < ' + str(end)
    try:
        csor2.execute(sql)
        conn2.commit()
    except Exception as e:
        #     # 发生错误时回滚
        print e

    res = csor2.fetchall()
    for cap in res:
        id = cap[0]
        content = cap[1]
        content = re.sub(u'www.{0,15}com', "", content.lower())
        content = re.sub(u'wwww.{0,15}ｃ.{1,2}м', "", content)
        updateContentById(id, content)

    csor2.close()
    conn2.close()

def insertBookWithConn(bookObj, conn2 = None,csor2 = None):

    if not conn2 or not csor2:
        conn2,csor2 = getDushuConnCsor()

    userId = random.randint(1,50)

    updateTime = int(time.time())

    import hashlib

    m2 = hashlib.md5()
    forDigest = bookObj['title'] + u'#' + bookObj['author']
    # forDigest = u'总裁我很忙#jxj季'
    m2.update(forDigest.encode('utf-8'))
    digest =  m2.hexdigest()
    bookObj['digest'] = digest

    if not bookObj.has_key('source'):
        bookObj['source'] = 'yisouxiaoshuo'

    try:
        csor2.execute('insert  ' + db_dushu +
          '(categoryCode,typeCode,category,type,userId,title,subtitle,imgUrl,author,updateTime' \
          ",rawUrl,source,digest,status,viewNum, chapterNum, bookType) values" \
          "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" \
          , (bookObj['categoryCode'],bookObj['typeCode'], bookObj['category'], bookObj['type'], userId,bookObj['title']
             ,bookObj['subtitle'],bookObj['imgUrl'],bookObj['author'],updateTime, bookObj['rawUrl']
             ,bookObj['source'],digest, 11,bookObj['viewNum'],bookObj['chapterNum'],bookObj['bookType']))
        # csorDoc.execute('update cn_dushu_book set subtitle = %s where digest = %s'
        #   , (bookObj['subtitle'],digest))
        conn2.commit()
        print 'succ book, ',bookObj['title']
    except Exception as e:
        #     # 发生错误时回滚
        print 'update rollback; maybe exists， ', bookObj['rawUrl'],e
        if conn2:
            try:
                conn2.rollback()
            except Exception as ee:
                print 'rollback error : ',bookObj['rawUrl']

        if u'完结' == bookObj['bookType']:
            updateBookTypeByRawUrl(bookObj['bookType'], bookObj['rawUrl'])
            return None
        # @TODO 检查数量是否一致即可，数量《=库中 即可跳过
    # sql2 = 'select id from cn_dushu_book where rawUrl = "%s";' % (bookObj['rawUrl'])


    csor2.execute("select id from " + db_dushu + " where rawUrl = %s", (bookObj['rawUrl'],))
    conn2.commit()

    results = csor2.fetchall()

    if not results or len(results) < 1:
        return None
    else:
        bookObj['id'] = results[0][0]

    csor2.close()
    conn2.close()

    return bookObj

def delBookById(bookId):
    conn2, csor2 = getDushuConnCsor()

    bookId = int(bookId)
    sql = "delete from " + db_dushu + " where id = %d" % bookId
    try:
        csor2.execute(sql)
        conn2.commit()
    except Exception as e:
        #     # 发生错误时回滚
        print 'mysql ex: ', e
        if conn2:
            try:
                conn2.rollback()
            except Exception as ee:
                print 'rollback error : ', bookId

    csor2.close()
    conn2.close()

def loadExistsSQId():
    conn2, csor2 = getDushuConnCsor()

    bloom = getBloom(200000)
    csor2.execute("select source from cn_dushu_book where source like 'shuqi%' and id < 127400;")#id > %s and id < %s", (step, step + carry))
    conn2.commit()
    caps = csor2.fetchall()
    for s in caps:
        bloom.add(s)
    dumpBloomToFile(bloom, 'local/BooksBloomDump')

    csor2.close()
    conn2.close()

    return bloom

def getExistsCapsRawUrlId(bookId):

    conn,csor = getDushuConnCsor()

    checkCapsSql = 'select id,rawUrl from cn_dushu_acticle where bookId = %d' % (bookId)
    try:
        csor.execute(checkCapsSql)
        conn.commit()
        results = csor.fetchall()

        if not results or len(results) < 1:
            print 'no caps,, bookId：', bookId
            return None
        else:
            return results
    except Exception as e:
        #     # 发生错误时回滚
        print 'check cap count failed ,skip', e

    csor.close()
    conn.close()


def updateContentById(id, content):

    conn,csor = getDushuConnCsor()

    # sql = "update cn_dushu_acticle set content = %s where id = %s " % (content, str(id))
    try:
        csor.execute( "update cn_dushu_acticle set content = %s where id = %s ", (content, id))
        conn.commit()
        print id, ' succ cap, ', content[0: 15]
    except Exception as e:
        #     # 发生错误时回滚
        print 'update error ',e
        if conn:
            try:
                conn.rollback()
            except Exception as ee:
                print 'rollback error : '


    csor.close()
    conn.close()


def insertCapWithCapObj2(capObj, conn2 = None, csor2 = None):

    if not conn2 or not csor2:
        conn2,csor2 = getDushuConnCsor()
    # sql = "insert ignore cn_dushu_acticle (title,rawUrl,source,content,bookId,idx,digest,size,bookUUID) values" \
    #       "('%s','%s','%s','%s',%d,%d,'%s', %d, '%s')" % (
    #           capObj['title'], capObj['rawUrl'], capObj['source'], capObj['content']
    #           , capObj['bookId'], capObj['idx'], capObj['digest'], capObj['size'], capObj['bookUUID'])
    try:
        csor2.execute("insert " + db_acticle + " (bookId,idx,digest,bookUUID,title,size) values" \
          "(%s,%s,%s,%s,%s,%s)" , (capObj['bookId'], capObj['idx'], capObj['digest'], capObj['bookUUID'], capObj['title'], capObj['size']))
        # csor2.execute("update cn_dushu_acticle set title = %s, size= %s where digest = %s" , (capObj['title'], capObj['size'], capObj['digest'] ))
        conn2.commit()
        print 'scap， ', capObj['source']+":" + str(capObj['idx']), ', content: ', capObj['content'][0:15]



    except Exception as e:
        #     # 发生错误时回滚
        print 'mysql ex: ', e
        if conn2:
            try:
                conn2.rollback()
            except Exception as ee:
                print 'rollback error : ', capObj['bookId']
        return None
    try:
        csor2.execute("select id,bookId from " + db_acticle + " where digest = %s;", (capObj['digest'],))
        conn2.commit()

        sqlObj = csor2.fetchone()
        capId = sqlObj[0]
        bookId = sqlObj[1]

        if bookId != capObj['bookId']:
            print 'update bookId',capId
            # 如果已存在，且bookId不对，更新下，防止错误cap占坑
            csor2.execute("update " + db_acticle + " set bookId = %s where id = %s;", (capObj['bookId'], capId))
            conn2.commit()

        capObj['id'] = capId
        return capId
    except Exception as e:
        #     # 发生错误时回滚
        print 'mysql ex2: ', e
        if conn2:
            try:
                conn2.rollback()
            except Exception as ee:
                print 'rollback error : ', capObj['bookId']
        return None

    csor2.close()
    conn2.close()


def insertCapWithCapObj(capObj, conn2, csor2):
    if not conn2 or not csor2:
        conn2,csor2 = getDushuConnCsor()


    # sql = "insert ignore cn_dushu_acticle (title,rawUrl,source,content,bookId,idx,digest,size,bookUUID) values" \
    #       "('%s','%s','%s','%s',%d,%d,'%s', %d, '%s')" % (
    #           capObj['title'], capObj['rawUrl'], capObj['source'], capObj['content']
    #           , capObj['bookId'], capObj['idx'], capObj['digest'], capObj['size'], capObj['bookUUID'])
    try:
        csor2.execute("insert cn_dushu_acticle (bookId,idx,digest,bookUUID,title,size) values" \
          "(%s,%s,%s,%s,%s,%s)" , (capObj['bookId'], capObj['idx'], capObj['digest'], capObj['bookUUID'], capObj['title'], capObj['size']))
        # csor2.execute("update cn_dushu_acticle set title = %s, size= %s where digest = %s" , (capObj['title'], capObj['size'], capObj['digest'] ))
        conn2.commit()
        print 'scap， ', capObj['source']+":" + str(capObj['idx']), ', content: ', capObj['content'][0:15]



    except Exception as e:
        #     # 发生错误时回滚
        print 'mysql ex: ', e
        if conn2:
            try:
                conn2.rollback()
            except Exception as ee:
                print 'rollback error : ', capObj['bookId']
        return None
    try:
        csor2.execute("select id,bookId from cn_dushu_acticle where digest = %s;", (capObj['digest'],))
        conn2.commit()

        sqlObj = csor2.fetchone()
        capId = sqlObj[0]
        bookId = sqlObj[1]

        if bookId != capObj['bookId']:
            print 'update bookId',capId
            # 如果已存在，且bookId不对，更新下，防止错误cap占坑
            csor2.execute("update cn_dushu_acticle set bookId = %s where id = %s;", (capObj['bookId'], capId))
            conn2.commit()

        capObj['id'] = capId
        return capId
    except Exception as e:
        #     # 发生错误时回滚
        print 'mysql ex2: ', e
        if conn2:
            try:
                conn2.rollback()
            except Exception as ee:
                print 'rollback error : ', capObj['bookId']
        return None

    csor2.close()
    conn2.close()