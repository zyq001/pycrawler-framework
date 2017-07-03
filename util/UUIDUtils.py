#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
import hashlib
import uuid


def getMD5(forDigest):
    '''
    MD5
    :param forDigest: unicode格式的str
    :return: str格式
    '''

    m2 = hashlib.md5()
    if isinstance(forDigest, unicode):
        m2.update(forDigest.encode('utf-8'))
    elif isinstance(forDigest, str):
        m2.update(forDigest)

    digest = m2.hexdigest()
    return digest

def getUUID():
    return str(uuid.uuid1()).replace('-', '')

def getBookDigest(bookObj, author = None, title = None):
    if not author:
        author = bookObj['author']

    if not title:
        title = bookObj['title']

    forDigest = title + u'#' + author

    return getMD5(forDigest)



def getCapDigest(bookObj, capObj, j):
    forDigest = bookObj['rawUrl'] + capObj['title'] + u'#' + str(j)

    return getMD5(forDigest)

if __name__ == '__main__':
    print getMD5('algorithm=MD5&apiKey=001&appId=26&bookId=68158&bundle=com.mftxtxs.novel&channelId=2&chapterId=1&nouce=dfe149b1a6f94a188b6f3832b3021086&osType=2&sid=SID&timestamp=1498815922012&userId=201706202002092307744175&userType=0&v=1&version=3.4.0&9dbfbfd095fe6648cbc14a8d19952791')