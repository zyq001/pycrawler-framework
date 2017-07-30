#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
source字段，例：shuqi001、mianfei001
@author: zyq
'''
from dao.connFactory import getDushuConnCsor


class SourceIdBloom:
    def __init__(self):
        self.ids = set()


    def loadDid(self):
        conn, csor = getDushuConnCsor()

        csor.execute("select source from cn_dushu_book;")
        conn.commit()
        ss = csor.fetchall()
        [self.ids.add(sid[0]) for sid in ss]

        csor.execute("select sid from shuqi_deleted_ids;")
        conn.commit()
        ss = csor.fetchall()
        [self.ids.add('shuqi' + str(sid[0])) for sid in ss]

        csor.close()
        conn.close()

    def contains(self, iid):
        return iid in self.ids

    def add(self, iid):
        self.ids.add(iid)

srcIdBloom = SourceIdBloom()
srcIdBloom.loadDid()