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
db_typeBook = 'cn_dushu_typebook'

def getIdsByType(confType):
    conn,csor = getDushuConnCsor()

    try:
        csor.execute("select ids from " + db_typeBook + " where type = %s", (confType, ) )
        conn.commit()
    except Exception as e:
        myLogging.warning('get bookType exception: '+ str(e))

    ids = csor.fetchone()[0]
    csor.close()
    conn.close()
    return ids

def updateIdsByType(confType, ids):
    conn,csor = getDushuConnCsor()

    try:
        csor.execute("update " + db_typeBook + ' set ids = %s  where type = %s', (ids, confType ))
        conn.commit()
    except Exception as e:
        myLogging.warning('update bookType exception: '+ str(e))

    csor.close()
    conn.close()
    # return ids

# if __name__ == '__main__':
#     delBookById(227921)