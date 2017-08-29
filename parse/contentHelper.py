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

class QQNumFliter(BaseFliter):
    def parse(self, content):

        noises = [
            '读者交流群\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            '书友群\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            'VIP书友群\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            'vip书友群\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            '书友群\d\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            '群号码\d\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            '作者交流群\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            'QQ群号码\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            'qq群号码\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            '书友QQ群\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            'QQ群\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            '书友qq群\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            'qq群\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            '交流群\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            '购书群\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            '企鹅聊天群\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            '聊天群\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            '(请)?加群\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            '(微)?v?V?信号\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            '欢迎加入讨论\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            '(请)?加入讨论\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            '(请)?\+?(加)?(作者)?(读者)?(小说)?(讨论)?(扣){0,2}q{0,2}Q{0,2}(扣){0,2}(企鹅)?群\d?(一)?(二)?(三)?(四)?(号)?(是)?\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            '(请)?\+?(加)?(作者)?(读者)?(小说)?(讨论)?(扣){0,2}(q{1,2}|Q{1,2})(扣){0,2}(企鹅)?(群)?\d?(一)?(二)?(三)?(四)?(号)?(是)?\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            '(请)?\+?(加)?(作者)?(读者)?(小说)?(讨论)?(扣){0,2}(q{0,2}|Q{0,2})(扣){0,2}(企鹅)(群)?\d?(一)?(二)?(三)?(四)?(号)?(是)?\s*(：|:)?\s*\(?(（)?[0-9]+\)?(）)?',
            '书友群',
            '读者群',
            '作者群',
            '(期待)?大家(的)?加入',
            '欢迎加入'

        ]

        tails = [
            '移动用户请发送',
            '唯一指定空间网址',
            '空间网址',
            '敲门砖'
        ]

        import re
        if isinstance(content,unicode):
            content = content.encode('utf-8')
        for noise in noises:
            content = re.sub(noise, '', content)


        for tail in tails:
            index2 = content.find(tail)
            if index2 > 0:
                content = content[:index2]

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


def subTitleClean(content, fliterList = None):
    if not fliterList:
        fliterList = [QQNumFliter()]

    for fliter in fliterList:
        content = fliter.parse(content)

    return content

if __name__ == '__main':
    content = subTitleClean('群:579057153')