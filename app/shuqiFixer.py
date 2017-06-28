#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
import requests

from app.mianfeiTXTCrawler import handleByMTID, handleCapsByBookObj
from app.shuqiUpdater import updateByBookObj
from dao.connFactory import getDushuConnCsor
from dao.dushuService import delCapById
from dao.dushuShuqiService import getShuqiAllBookObjs, db_acticle


def digestFix(st = 200000, end = 2):
    conn,csor = getDushuConnCsor()

    csor.execute("SELECT id,rawUrl,chapNum from cn_dushu_book where rawUrl like"
                 " 'http://api.yingyangcan.com.cn/interface/ajax/book/getbaseinfo.ajax?%';")
    conn.commit()

    results = csor.fetchall()

    for book in results:
        bookId = book[0]
        rawUrl = book[1]
        chapNum = book[2]

        csor.execute('select count(*) from cn_dushu_acticle where bookId = %s;', (bookId,))
        conn.commit()
        nowCapNum = csor.fetchone()[0]
        # if nowCapNum >=


def fixUnFinished():
    conn, csor = getDushuConnCsor()

    csor.execute("SELECT id,rawUrl,chapterNum,source,digest from cn_dushu_book where rawUrl like"
                 " 'http://api.yingyangcan.com.cn/interface/ajax/book/getbaseinfo.ajax?%';")
    conn.commit()

    results = csor.fetchall()

    for book in results:
        bookId = book[0]
        rawUrl = book[1]
        chapNum = book[2]

        mid = book[3]
        if 'mianfeiTXT' in mid:
            mid = mid.replace('mianfeiTXT', '')

        bookDigest = book[4]

        bookObj = dict()
        bookObj['id'] = bookId
        bookObj['source'] = mid
        bookObj['digest'] = bookDigest
        bookObj['rawUrl'] = rawUrl

        csor.execute('select count(*) from cn_dushu_acticle where bookId = %s;', (bookId,))
        conn.commit()
        nowCapNum = csor.fetchone()[0]

        if nowCapNum < chapNum:
            handleCapsByBookObj(allowUpdate=True,bookObj=bookObj,count=chapNum, mid=mid )
            # handleByMTID(mid, allowUpdate=True)
#发现有一些id在oss中找不到，发现是因为重复入库导致，故删除oss中没有的id，然后更新图书和章节相关信息
def fixUnuploadedCaps():
    bookObjs = getShuqiAllBookObjs()
    conn,csor = getDushuConnCsor()
    for bookObj in bookObjs:

        csor.execute('select count(*) from ' + db_acticle + ' where bookId = %s ', (bookObj['id'], ))
        conn.commit()
        db_cap_count = csor.fetchone()[0]
        if db_cap_count <= bookObj['chapterNum']:
            continue

        csor.execute('select id from ' + db_acticle + ' where bookId = %s order by id desc', (bookObj['id'], ))
        conn.commit()
        cids = csor.fetchall()

        deleteCount = 0
        for cidL in cids:
            cid = cidL[0]
            ossUrl = 'http://dushu-content.oss-cn-shanghai.aliyuncs.com/' + str(cid) + '.json'
            r = requests.head(ossUrl)
            if r.status_code > 200:
                print 'bookId' + str(bookObj['id']) + ' cid: ' + str(cid) + ' status_code: ' + str(r.status_code)

                #从章节表中删除
                delCapById(cid)
                deleteCount = deleteCount + 1
            else:
                nowCapCount = len(cids) - deleteCount
                if bookObj['chapterNum'] <= nowCapCount:
                    break

        if deleteCount > 0:#有删除
            nowCapCount = len(cids) - deleteCount
            if bookObj['chapterNum'] == nowCapCount:
                continue #正好相等时两种情况：1，完结，应该没问题，暂不管；2，连载交给定时updater

            if bookObj['chapterNum'] < nowCapCount: #如果删除后章节还多，打日志,update
                print 'still more chapters, check bookId: ', str(bookObj['id'])

            # 删除后章节不够，update，
            elif bookObj['chapterNum'] > nowCapCount:
                bookObj['chapterNum'] = nowCapCount

            #update
            updateByBookObj(bookObj)

    csor.close()
    conn.close()

if __name__ == '__main__':
    # fixUnFinished()
    fixUnuploadedCaps()