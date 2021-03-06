#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
source字段，例：shuqi001、mianfei001
@author: zyq
'''
from dao.connFactory import getDushuConnCsor


class BookDiBloom:
    def __init__(self):
        self.ids = set()


    def loadDid(self):
        conn, csor = getDushuConnCsor()

        csor.execute("select digest from cn_dushu_book where operateStatus = 0;")
        conn.commit()
        ss = csor.fetchall()
        [self.ids.add(sid[0]) for sid in ss]


        csor.close()
        conn.close()

    def contains(self, iid):
        '''
        是否包含
        :param iid: id
        :return: true or false
        '''
        return iid in self.ids

    def add(self, iid):
        self.ids.add(iid)

bookDigestBloom = BookDiBloom()
bookDigestBloom.loadDid()