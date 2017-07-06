#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
import sys
import traceback

from app.QuanBenMianFeiCrawler import QuanBenCrawler
from app.mianfeiTXTNewFilder import findByIdRange
from util.logHelper import myLogging


def fromTopNBookIds():
    fbids = open('top5wBookIds.txt')
    bidsSet = set()
    while 1:
        bid = fbids.readline()
        if not bid:
            break
        bid = bid.replace('\n', '')
        bidsSet.add(bid)
    print 'load to dict uniq ' + str(len(bidsSet))
    for bid in bidsSet:
        try:
            QuanBenCrawler('576989a21b341116f654d84a').crawl(allowUpdate=False)

        except Exception as e:
            myLogging.error('bookId %s has exception: ' + traceback.format_exc(), bid)


if __name__ == '__main__':

    fromTopNBookIds()

    # st = 50000
    # end = 500000
    # if len(sys.argv) > 1:
    #     st = int(sys.argv[1])
    #     end = int(sys.argv[2])
    #
    # findByIdRange(st, end)