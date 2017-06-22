#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
from dao.connFactory import getDushuConnCsor


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

        csor.execute('select count(*) from cn_dushu_acticle where bookId = %s;', (bookId))
        conn.commit()
        nowCapNum = csor.fetchone()[0]
        # if nowCapNum >=