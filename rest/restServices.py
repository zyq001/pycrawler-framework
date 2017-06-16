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
from manager.Manager import Manager

urls = (
    # '/', 'index',
    '/ershoufang', 'ershoufang'
)

# render = web.template.render('templates/')

"""
Handles the GET/POST of image url to OCR result string.
"""


class ershoufang:
    # def initialize(self, *args, **kwargs):
    #     self.contentType = self.request.headers.get('Content-Type')

    def GET(self):
        return self.POST()

    def POST(self):
        web.header("Content-Type", "application/json; charset=UTF-8")
        response = {'code': 200, 'msg': 'ok'}

        inputParams = web.input(crawlerName="", crawler_count=1, output_count=1)
        if '' == inputParams.crawlerName:
            response['msg'] = 'no crawler name!'
            return response

        crawler_count = inputParams.crawler_count
        output_count = inputParams.output_count

        manager = Manager()

        # manager.start()

        if 'ershoufang' == inputParams.crawlerName:
            ershoufangCrawler = Ershoufang()
            manager.addCrawler(ershoufangCrawler, inputParams.crawler_count, inputParams.output_count)

        manager.start()
        # send response json
        # self.write(response)

        return response

class WebServer:

    def run(self, port=8000):
        app = web.application(urls, globals())
        web.httpserver.runsimple(app.wsgifunc(), ('0.0.0.0', port))


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
