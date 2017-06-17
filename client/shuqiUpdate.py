#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
追书旗上连载书的更新
@author: zyq
'''
import json

import requests

from dao.connFactory import getDushuConnCsor


def updateFromMysql():
    '''
        永远运行，从数据库中查询出于连载状态的小说，进行更新
    '''

    crawlInput = dict()
    crawlInput['crawlerName'] = 'shuqiById'
    data = dict()
    crawlInput['data']  = data

    conn,csor = getDushuConnCsor()

    csor.execute("SELECT source from cn_dushu_book where operateStatus = 0  AND bookType = '连载' and rawUrl like 'http://api.shuqireader.com/reader/bc_cover.php%';")
    conn.commit()

    ss = csor.fetchall()
    for source in ss:
        sid = source[0].replace('shuqi', '')
        if '' == sid:
            continue
        data['sid'] = sid

        try:
            r = requests.post('http://0.0.0.0:10008/simpleCrawler', data = json.dumps(crawlInput))
        # print 'dine id: ',sid, 'with response: ',
        except Exception as e:
            print 'sid: ',sid, ' done with exception: ', e.message



if __name__ == '__main__':
    while 1:
        updateFromMysql()