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
import traceback

import MySQLdb

from dao.aliyunOss import upload2Bucket
from dao.connFactory import getDushuConnCsor
from parse.easouParser import getAndParse
from util.UUIDUtils import getBookDigest
from util.logHelper import myLogging
from util.pyBloomHelper import getBloom, dumpBloomToFile

db_dushu = 'cn_dushu_book'
db_acticle = 'cn_dushu_acticle'

def getBookObjById(dbid):
    '''
    更加库中主键id获取book对象
    :param dbid: 
    :return: 
    '''
    conn,csor = getDushuConnCsor()
    dictCsor = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        dictCsor.execute("select * from " + db_dushu + " where id = %s", (dbid,))
        conn.commit()
    except Exception as e:
        myLogging.warning('update bookType exception: '+ str(e))
    bookObj = dictCsor.fetchoneDict()
    csor.close()
    conn.close()
    return bookObj

def updateBoostWithUpdateTime(dbid):
    '''
    更加库中主键id获取book对象
    :param dbid: 
    :return: 
    '''
    conn,csor = getDushuConnCsor()
    dictCsor = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        dictCsor.execute("update " + db_dushu + " set typeBoost = updateTime where id = %s", (dbid,))
        conn.commit()
    except Exception as e:
        myLogging.warning( 'update bookType exception: ' + str(e))
    bookObj = dictCsor.fetchoneDict()
    csor.close()
    conn.close()
    return bookObj

def updateBookTypeByRawUrl(type, rawUrl):
    conn, csor = getDushuConnCsor()
    try:
        csor.execute("update " + db_dushu + " set bookType = %s where rawUrl = %s", (type, rawUrl,))
        conn.commit()
    except Exception as e:
        myLogging.warning( 'update bookType exception: '+ str(e))

    csor.close()
    conn.close()

def updateOneFieldByOneField(upFieldName, upFieldValue, byFieldName, byFieldValue):
    conn, csor = getDushuConnCsor()
    try:
        csor.execute("update " + db_dushu + " set " + upFieldName + "  = %s, updateTime =  " + str(int(time.time()))  + " where " + byFieldName + " = %s",
                     ( upFieldValue, byFieldValue))
        conn.commit()
    except Exception as e:
        myLogging.warning( 'update bookType exception: ' + str(e))

    csor.close()
    conn.close()

def handleWebsiteNoise(begin, end):

    conn2,csor2 = getDushuConnCsor()

    sql = 'select id,content from cn_dushu_acticle where bookId = 960 and id > ' + str(begin) + ' and id < ' + str(end)
    try:
        csor2.execute(sql)
        conn2.commit()
    except Exception as e:
        #     # 发生错误时回滚
        myLogging.warning( e)

    res = csor2.fetchall()
    for cap in res:
        id = cap[0]
        content = cap[1]
        content = re.sub(u'www.{0,15}com', "", content.lower())
        content = re.sub(u'wwww.{0,15}ｃ.{1,2}м', "", content)
        updateContentById(id, content)

    csor2.close()
    conn2.close()

def insertBookWithConn(bookObj, allowUpdate = True, conn2 = None,csor2 = None):

    if not conn2 or not csor2:
        conn2,csor2 = getDushuConnCsor()

    userId = random.randint(1,50)

    updateTime = int(time.time())

    digest = getBookDigest(bookObj)
    bookObj['digest'] = digest

    if not bookObj.has_key('source'):
        bookObj['source'] = 'yisouxiaoshuo'

    try:
        csor2.execute('insert  ' + db_dushu +
          '(categoryCode,typeCode,category,type,userId,title,subtitle,imgUrl,author,updateTime' \
          ",rawUrl,source,digest,status,viewNum, chapterNum, bookType, size) values" \
          "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)" \
          , (bookObj['categoryCode'],bookObj['typeCode'], bookObj['category'], bookObj['type'], userId,bookObj['title']
             ,bookObj['subtitle'],bookObj['imgUrl'],bookObj['author'],updateTime, bookObj['rawUrl']
             ,bookObj['source'],digest, 11,bookObj['viewNum'],bookObj['chapterNum'],bookObj['bookType'],bookObj['size']))
        # csorDoc.execute('update cn_dushu_book set subtitle = %s where digest = %s'
        #   , (bookObj['subtitle'],digest))
        conn2.commit()
        myLogging.info( 'succ book, ' + unicode(bookObj['title']).encode('utf-8'))
    except Exception as e:
        #     # 发生错误时回滚
        myLogging.warning( 'update rollback; maybe exists，rawUrl: %s, err:  %s', bookObj['rawUrl'] , traceback.format_exc())
        if conn2:
            try:
                conn2.rollback()
            except Exception as ee:
                myLogging.error('rollback error : ' + bookObj['rawUrl'])

        if u'完结' == bookObj['bookType']:
            updateBookTypeByRawUrl(bookObj['bookType'], bookObj['rawUrl'])
            # return None #有bug
        if not allowUpdate:
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



def getCapIdxsByBookId(bookId):
    conn,csor = getDushuConnCsor()
    idxs = set()

    csor.execute('select idx from ' + db_acticle + " where bookId = %s", (bookId,))
    conn.commit()

    results = csor.fetchall()
    for capObj in results:
        idxs.add(capObj[0])
    csor.close()
    conn.close()

    return idxs

def getChapTitlesByBookId(bookId):
    conn,csor = getDushuConnCsor()
    titles = set()

    csor.execute('select title from ' + db_acticle + " where bookId = %s", (bookId,))
    conn.commit()

    results = csor.fetchall()
    for capObj in results:
        titles.add(capObj[0])
    csor.close()
    conn.close()

    return titles

def delCapById(cid):
    conn2, csor2 = getDushuConnCsor()

    try:
        csor2.execute("delete from " + db_acticle + " where id = %s", (cid, ))
        conn2.commit()
    except Exception as e:
        #     # 发生错误时回滚
        myLogging.error( 'mysql ex: ' +  str(e))
        if conn2:
            try:
                conn2.rollback()
            except Exception as ee:
                myLogging.error('rollback error : ' + str(cid))

    csor2.close()
    conn2.close()


def delBookById(bookId):
    conn2, csor2 = getDushuConnCsor()

    #将删除的书记录到deleted_ids表中
    csor2.execute('select rawUrl,source from ' + db_dushu + ' where id = %s', (bookId,))
    conn2.commit()
    bookObj = csor2.fetchone()
    if not bookObj:
        return
    rawUrl = bookObj[0]
    source = bookObj[1].replace('shuqi', '')
    if 'shuqireader' in rawUrl:
        csor2.execute('insert into shuqi_deleted_ids (id, sid) VALUEs (%s, %s)', (bookId, source))
        conn2.commit()
    elif 'yingyangcan' in rawUrl:
        csor2.execute('insert into mianfei_deleted_ids (id, mid) VALUEs (%s, %s)', (bookId, source))
        conn2.commit()


    bookId = int(bookId)
    # sql = "delete from " + db_dushu + " where id = %d" % bookId
    try:
        csor2.execute("delete from " + db_dushu + " where id = %s", (bookId, ))
        conn2.commit()
    except Exception as e:
        #     # 发生错误时回滚
        myLogging.error( e)
        if conn2:
            try:
                conn2.rollback()
            except Exception as ee:
                myLogging.error(e)

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
            myLogging.warning( 'no caps,, bookId：' + str(bookId))
            return None
        else:
            return results
    except Exception as e:
        #     # 发生错误时回滚
        myLogging.error(e)

    csor.close()
    conn.close()


def updateContentById(id, content):

    conn,csor = getDushuConnCsor()

    # sql = "update cn_dushu_acticle set content = %s where id = %s " % (content, str(id))
    try:
        csor.execute( "update cn_dushu_acticle set content = %s where id = %s ", (content, id))
        conn.commit()
        myLogging.info(str(id) + ' succ cap, ' + content[0: 15])
    except Exception as e:
        #     # 发生错误时回滚
        myLogging.error(e)
        if conn:
            try:
                conn.rollback()
            except Exception as ee:
                myLogging.error(ee)

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
        myLogging.info('scap， ' + capObj['source'] + ":" + str(capObj['idx']))

    except Exception as e:
        #     # 发生错误时回滚
        myLogging.error(e)
        if conn2:
            try:
                conn2.rollback()
            except Exception as ee:
                myLogging.error(ee)
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
        myLogging.error(e)
        if conn2:
            try:
                conn2.rollback()
            except Exception as ee:
                myLogging.error(ee)
        return None

    csor2.close()
    conn2.close()


def insertCapWithCapObj(capObj, conn2 = None, csor2 = None):
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
        myLogging.info('scap， ' +  ":" + str(capObj['idx']) )
            # , ', content: ', capObj['content'][0:15]



    except Exception as e:
        #     # 发生错误时回滚
        myLogging.error(e)
        if conn2:
            try:
                conn2.rollback()
            except Exception as ee:
                myLogging.error(ee)
        return None
    try:
        csor2.execute("select id,bookId from cn_dushu_acticle where digest = %s;", (capObj['digest'],))
        conn2.commit()

        sqlObj = csor2.fetchone()
        capId = sqlObj[0]
        bookId = sqlObj[1]

        if bookId != capObj['bookId']:
            myLogging.info( 'update bookId' + str(capId))
            # 如果已存在，且bookId不对，更新下，防止错误cap占坑
            csor2.execute("update cn_dushu_acticle set bookId = %s where id = %s;", (capObj['bookId'], capId))
            conn2.commit()

        capObj['id'] = capId
        return capId
    except Exception as e:
        #     # 发生错误时回滚
        myLogging.error(e)
        if conn2:
            try:
                conn2.rollback()
            except Exception as ee:
                myLogging.error(ee)
        return None

    csor2.close()
    conn2.close()

def deleteChapsLargerThanIdx(bookId, idx):
    '''
    删除章节表中所有大于此idx的
    :param bookId: 
    :param idx: 
    :return: 
    '''
    conn,csor = getDushuConnCsor()
    try:
        csor.execute('delete from ' + db_acticle + " where bookId = %s and idx > %s", (bookId, idx))
        conn.commit()
    except Exception as e:
        myLogging.warning(e)

    csor.close()
    conn.close()

def getChapObjByBookIdChapTitle(bookId, title):
    '''
    删除章节表中所有大于此idx的
    :param bookId: 
    :param idx: 
    :return: 
    '''
    conn,csor = getDushuConnCsor()
    dictCsor = conn.cursor(MySQLdb.cursors.DictCursor)

    try:
        dictCsor.execute('select *  from ' + db_acticle + " where bookId = %s and title = %s", (bookId, title))
        conn.commit()
    except Exception as e:
        myLogging.warning(e)

    chapObj = dictCsor.fetchoneDict()

    csor.close()
    conn.close()

    return chapObj


def getLatestChapByBookId(bookId):
    conn,csor = getDushuConnCsor()

    dictCsor = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        dictCsor.execute("select * from " + db_acticle + " where bookId = %s order by id desc limit 1;", (bookId,))
        conn.commit()
    except Exception as e:
        myLogging.warning('getLatestChapByBookId exception: '+ str(e))
    bookObj = dictCsor.fetchoneDict()
    csor.close()
    conn.close()
    return bookObj

if __name__ == '__main__':
    delBookById(227921)