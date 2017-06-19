#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
import hashlib


def getBookDigest(bookObj, author = None, title = None):
    if not author:
        author = bookObj['author']

    if not title:
        title = bookObj['title']

    m2 = hashlib.md5()
    forDigest = title + u'#' + author
    m2.update(forDigest.encode('utf-8'))
    digest = m2.hexdigest()
    return digest


def getCapDigest(bookObj, capObj, j):
    m2 = hashlib.md5()
    forDigest = bookObj['digest'] + capObj['title'] + u'#' + str(j)
    m2.update(forDigest.encode('utf-8'))
    digest = m2.hexdigest()
    return digest