#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
import MySQLdb

from app.fixer import newLineFixer
from dao.connFactory import getDushuConnCsor
from dao.dushuService import db_dushu, updateOneFieldByOneField
from parse.contentHelper import subTitleClean
from util.logHelper import myLogging


def cleanSubtitle():
    conn, csor = getDushuConnCsor()
    dictCsor = conn.cursor(MySQLdb.cursors.DictCursor)
    bookId = 2584584
    carry = 50000
    while bookId < 2590000:
        try:
            dictCsor.execute('select id,subtitle  from ' + db_dushu
                             + " where id >= %s and id <= %s and subtitle REGEXP '[0-9]{5,20}'", (bookId, bookId + carry))
            conn.commit()

            books = dictCsor.fetchallDict()
            for book in books:
                newSubtitle = subTitleClean(book['subtitle'])
                if not newSubtitle == book['subtitle'].encode('utf-8'):
                    myLogging.info('bookId %s update from %s to %s', book['id'], book['subtitle'].encode('utf-8'), newSubtitle)
                    updateOneFieldByOneField('subtitle', newSubtitle, 'id', book['id'])

        except Exception as e:
            myLogging.warning(e)
        bookId += carry
    chapObj = dictCsor.fetchoneDict()

    csor.close()
    conn.close()

if __name__ == '__main__':
    # newLineFixer()
    # content = subTitleClean('群:579057153')
    cleanSubtitle()