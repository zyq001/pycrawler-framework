#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Config import bloomDumpCapsName, bloomDumpBooks


def getBloom(cap=10000000):

    from pybloom import BloomFilter
    f = BloomFilter(capacity=cap, error_rate=0.001)
    return f


def loadBloomFromFile(fileName = bloomDumpCapsName):
    from pybloom import BloomFilter
    try:
        bloom = BloomFilter.fromfile(open(fileName, 'r'))
    except IOError as er:
        print 'load bloom from file fail, return null', er
        return None
    except Exception as e:
        print 'load bloom from file got exception, return null', e
        return None
    return bloom


def loadBloomBooks(fileName = bloomDumpBooks):
    return loadBloomFromFile(fileName)


def dumpBloomToFile(bloom, fileName = bloomDumpCapsName):
    bloom.tofile(open(fileName, 'w'))

