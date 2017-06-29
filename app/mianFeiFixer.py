#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
from app.mianfeiTXTCrawler import handleByMTID, handleCapsByBookObj
from dao.connFactory import getDushuConnCsor
from dao.dushuShuqiService import getShuqiIdRawUrlAsBookObjs


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

# def fixCapDigest():
#     books = getShuqiIdRawUrlAsBookObjs()
#     for bookObj in books:
#         bookId = bookObj['id']
#

if __name__ == '__main__':
    fixUnFinished()