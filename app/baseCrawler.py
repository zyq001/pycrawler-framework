#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
基类爬虫
zyq

'''
import abc


class BaseCrawler:

    @abc.abstractmethod
    def init(self, data = None):
        print 'init'

    @abc.abstractmethod
    def crawl(self):
        print 'crawling,,'

    @abc.abstractmethod
    def output(self):
        print 'Persistence'

