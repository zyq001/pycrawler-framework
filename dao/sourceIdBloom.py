#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
单例保存书旗所有的主键id,
书id，不需要bloom了，dict就够了
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

    def contains(self, iid):
        return iid in self.ids

    def add(self, iid):
        self.ids.add(iid)

sourceIdBloom = SourceIdBloom()
sourceIdBloom.loadDid()