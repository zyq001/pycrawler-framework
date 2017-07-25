#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
过滤内容的乱码或者其他字符：换行符等
@author: zyq
'''
import abc


class BaseFliter():
    @abc.abstractmethod
    def parse(self, content):
        pass

class NewLineFliter(BaseFliter):
    def parse(self, content):
        content = content.replace('<br>', '</p><p>')\
            .replace('\\r\\n', '</p><p>').replace('\r\n', '</p><p>')\
            .replace('\\n', '</p><p>').replace('\n', '</p><p>')\
            # .replace('\n', '</p><p>')
        if content.startswith('</p>'):
            content = content[4:]
        if content.endswith('<p>'):
            content = content[0:-3]
        if not content.startswith('<p>'):
            content = '<p>' + content
        if not content.endswith('</p>'):
            content =  content +'</p>'

        return content

defaultFliterList = [NewLineFliter()]

def textClean(content, fliterList = None):
    if not fliterList:
        global defaultFliterList
        fliterList = defaultFliterList
    for fliter in fliterList:
        content = fliter.parse(content)

    return content