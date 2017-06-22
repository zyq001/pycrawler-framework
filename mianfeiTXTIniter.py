#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
import sys

from app.mianfeiTXTNewFilder import findByIdRange

if __name__ == '__main__':


    st = 50000
    end = 500000
    if len(sys.argv) > 1:
        st = int(sys.argv[1])
        end = int(sys.argv[2])

    findByIdRange(st, end)