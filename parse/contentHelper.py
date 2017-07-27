#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
过滤内容的乱码或者其他字符：换行符等
@author: zyq
'''
import abc
import re

from local.easou.easouLocal import loadRules
# from parse.easouParser import rules

sitesRules = loadRules() #各个网站的正文、噪声等规则



def cleanTailHeadNoise(content):

    for host in sitesRules:
        content = cleanSiteNoisesByHost( content, host)

    content =  cleanCommonSitesNoises(content)
    content =  content.strip().strip(u'，').strip(',').strip('!').strip('.').strip(u'！')\
        .strip(u'。').strip(u'：').strip(':').strip(';').strip(u'；')

    return content

def cleanTailHead(urlhost, content):
    # rules = loadRules()
    content = cleanSiteNoisesByHost(content, urlhost)

    return cleanCommonSitesNoises(content)


def cleanCommonSitesNoises(content):
    # 清理通用噪声
    common = sitesRules['common']
    head = common['head']
    if head and len(head) > 0:
        index = content.find(head)
        if index > 0:
            content = content[index + len(head):]
    tails = common['tail']
    if tails and len(tails) > 0:
        for tail in tails:
            index2 = content.find(tail)
            if index2 > 0:
                content = content[:index2]
    noise = common['noise']
    if noise and len(noise) > 0:
        for n in noise:
            content = re.sub(n.lower(), "", content.lower())

    # 清理多余的回车和换行
    content = content.replace(u'\n\n', u'\n').replace(u'<br><br>', u'<br>').replace(u'<br\><br\>', u'<br\>')
    return content


def cleanSiteNoisesByHost(content, urlhost):
    if not sitesRules.has_key(urlhost):
        return content
    host = sitesRules[urlhost]
    head = host['head']
    if head and len(head) > 0:
        index = content.find(head)
        if index > 0:
            content = content[index + len(head):]
    tail = host['tail']
    if tail and len(tail) > 0:
        if not isinstance(tail, list):
            tail = [tail]
        for tl in tail:
            index = content.find(tl)
            if index > 0:
                content = content[:index]
    noise = host['noise']
    if noise and len(noise) > 0:
        for n in noise:
            content = re.sub(n, "", content)

    return content


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


class NoiseFliter(BaseFliter):
    def parse(self, content):

        return cleanTailHeadNoise(content)




defaultFliterList = [ NoiseFliter(), NewLineFliter()]

def textClean(content, fliterList = None):
    if not fliterList:
        global defaultFliterList
        fliterList = defaultFliterList
    for fliter in fliterList:
        content = fliter.parse(content)

    return content

