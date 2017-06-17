#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''

import ctypes
import json
import os, uuid, StringIO

import cStringIO
import urllib

# from Pillow import Image
import web
# from tesserocr import PyTessBaseAPI
import tesserocr

from PIL import Image

from app.ershoufang import Ershoufang
from manager.Manager import Manager, crawlManager
from manager.Task import Task
from rest.util.webpyHelper import getParams

urls = (
    # '/', 'index',
    '/simpleCrawler', 'SimpleCrawler'
)

# render = web.template.render('templates/')

"""
Handles the GET/POST of image url to OCR result string.
"""


class SimpleCrawler:
    # def initialize(self, *args, **kwargs):
    #     self.contentType = self.request.headers.get('Content-Type')

    def GET(self):
        return self.POST()

    def POST(self):
        web.header("Content-Type", "application/json; charset=UTF-8")
        response = {'code': 200, 'msg': 'ok'}
        try:
            params = getParams(web, crawlerName="", crawler_count=1, output_count=1, data = None)

            manager = crawlManager
            if not manager.crawlers.has_key(params['crawlerName']):
                response['msg'] = 'no crawler name!'
                return response

            crawler = manager.crawlers[params['crawlerName']]

            if params['data']:
                crawler.init(params['data'])

            task = Task(crawler, params['crawler_count'], params['output_count'])
            task.start()
        except Exception as e:
            response['msg'] = unicode(e)

        return response

class WebServer:

    def run(self, port=8000):
        app = web.application(urls, globals())
        web.httpserver.runsimple(app.wsgifunc(), ('0.0.0.0', port))


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
