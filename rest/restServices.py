#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''

import json

import web
from dao.ershoufangService import getChartAsStr
from exception.InputException import InputException
from manager.Manager import  crawlManager
from manager.Task import Task
from rest.util.webpyHelper import getParams

urls = (
    '/fang', 'Fang',
    '/', 'Index',
    '/search', 'Search',
    '/simpleCrawler', 'SimpleCrawler'
)

# render = web.template.render('templates/')

"""
Handles the GET/POST of image url to OCR result string.
"""

class Index:

    def Get(self):
        return 'hello'
    def POST(self):
        return 'hello'

class Search:
    def Get(self):
        return self.POST()

    def POST(self):
        web.header("Content-Type", "application/json; charset=UTF-8")
        response = {'code': 200, 'msg': 'ok'}
        respData = []
        try:
            params = getParams(web, name="", andCrawl=False, crawler_count=1, top=5, output_count=1, crawlerName = 'mianFeiTXT')

            if '' == params['name']:
                raise InputException('no input search name')

            manager = crawlManager
            if not manager.crawlers.has_key(params['crawlerName']):
                response['msg'] = 'no crawler name!'
                return response
            for crawlerName in params['crawlerName'].split(','):
                crawler = manager.crawlers[crawlerName]()

                searchResult = crawler.search(params['name'], params['top'])
                if params['andCrawl']:
                    for book in searchResult:
                        crawler.init(book)
                        task = Task(crawler, params['crawler_count'], params['output_count'])
                        task.start()
                respData.append({'crawlerName': crawlerName, 'books': searchResult})

        except Exception as e:
            response['msg'] = unicode(e)
            response['code'] = 500

        response['data'] = respData
        return json.dumps(response)

class Fang:

    def GET(self):
        web.header("Content-Type", "text/html; charset=UTF-8")
        return getChartAsStr()
        # return self.POST()

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

            crawler = manager.crawlers[params['crawlerName']]() #注意最后的小括号，是利用元类创建一个新的实例

            if params['data']:
                crawler.init(params['data'])

            task = Task(crawler, params['crawler_count'], params['output_count'])
            task.start()
        except Exception as e:
            response['msg'] = unicode(e)
            response['code'] = 500

        return json.dumps(response)

class WebServer:

    def run(self, port=8000):
        app = web.application(urls, globals())
        web.httpserver.runsimple(app.wsgifunc(), ('0.0.0.0', port))


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
