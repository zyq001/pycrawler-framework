##!/usr/bin/python
# -*- coding: UTF-8 -*-
import hashlib
import json
import random
import traceback
from urllib import quote

import MySQLdb
import time

from Config import EADHOST, EADPASSWD, OSSINTERNALENDPOINT, OSSUSER, OSSPASSWD, CapsBaseUrl, MianFeiTXTBookDetailUrl, \
    MianFeiContentBaseUrl, MianFeiTXTBaseUrl, MianFeiTXTSearchBaseUrl, MINCHAPNUM
# from easouCrawl import insertCapWithCapObj
# from framework.htmlParser import getSoupByStr
# from networkHelper import getContentWithUA
from app.baseCrawler import BaseCrawler
from dao.aliyunOss import upload2Bucket
from dao.dushuService import insertCapWithCapObj, getCapIdxsByBookId
from exception.InputException import InputException
from shuqi import insertBookWithConn
from util.UUIDUtils import getCapDigest
from util.htmlHelper import getSoupByStr, getSoupByUrl
from util.logHelper import myLogging
from util.networkHelper import getContentWithUA

ua = 'Mozilla/5.0 (Linux; U; Android 4.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13'
capListAPIDeviceInfo = '&soft_id=1&ver=110817&platform=an&placeid=1007&imei=862953036746111&cellid=13&lac=-1&sdk=18&wh=720x1280&imsi=460011992901111&msv=3&enc=666501479540451111&sn=1479540459901111&vc=e8f2&mod=M3'


# from DBUtils.PooledDB import PooledDB

# pool2 = PooledDB(creator=MySQLdb, mincached=1, maxcached=1,
#                 host=EADHOST, port=3306, user="ead",
#                 passwd=EADPASSWD, db="dushu", use_unicode=True, charset='utf8')
# conn2 = pool2.connection()
# csor2 = conn2.cursor()

# conn.set_character_set('utf8')
# csor2.execute('SET NAMES utf8')
# csor2.execute("SET CHARACTER SET utf8")
# csor2.execute("SET character_set_connection=utf8")


# def getBucket():
#     import oss2
#
#     # endpoint = OSSINTERNALENDPOINT  # 假设你的Bucket处于杭州区域
#     endpoint = OSSINTERNALENDPOINT  # 假设你的Bucket处于杭州区域
#
#     auth = oss2.Auth(OSSUSER, OSSPASSWD)
#     bucket = oss2.Bucket(auth, endpoint, 'dushu-content')
#
#     return bucket
#
# bucket = getBucket()
#
# def upload2Bucket(id, obj):
#
#     try:
#         bucket.put_object(id, obj)
#         # print 'succ upload ',id
#     except Exception as e:
#         print id, ' upload faild ',e


def handleByMTID(mid, allowUpdate = True):
    # baseUrl = MianFeiTXTBaseUrl
    # capListBaseUrl = CapsBaseUrl + str(mid) \
    #                  +'&pageindex=1&pagesize=100000000'
    # capContentBaseUrl = '%s' % MianFeiContentBaseUrl  #2&contentid=171117'
    # bookDetailUrl = MianFeiTXTBookDetailUrl
    bookObj, count = getBookObj(allowUpdate, mid)

    if not bookObj:
        return

    handleCapsByBookObj(allowUpdate, bookObj, count, mid)


def handleCapsByBookObj(allowUpdate, bookObj, count, mid, startCapIdx = 1):
    capIdxs = set()
    if allowUpdate:
        capIdxs = getCapIdxsByBookId(bookObj['id'])  # 已在库中的章节下标

    # myBookId = bookObj['id']
    #
    # startCap = time.time()
    crawlParseSpent = 0
    insertCap = 0
    uploadCap = 0
    succCapTimes = 1
    resIdx = count
    for cid in range(startCapIdx, count + 1):
        try:

            if allowUpdate:
                if cid in capIdxs:
                    continue  # 该章节已在库中，跳过
                # else:
                #     startCap = time.time()

            befCrawl = time.time()
            succCapTimes = succCapTimes + 1

            capContentUrl = MianFeiContentBaseUrl + str(cid) + '&contentid=' + str(mid)
            capContent = getContentWithUA(capContentUrl, ua)
            if not capContent:
                capContent = getContentWithUA(capContentUrl, ua)
            # capContent = capContent.replace(r'\r', '').replace(r'\n', '')
            capListJsonObj = json.loads(capContent, strict=False)
            if not (capListJsonObj['status'] == 1000):
                capListJsonObj = json.loads(capContent)
                if not (capListJsonObj['status'] == 1000 and capListJsonObj['message'] == u'成功'):
                    resIdx = min(cid, resIdx)
                    continue

            capObj = dict()
            orgContent = capListJsonObj['data']['chapter']
            contentSoup = getSoupByStr(orgContent)
            if not contentSoup or '' == orgContent or len(orgContent) < 1:
                myLogging.error('chap content null ,skip, capId:', str(cid), ' mid: ',str(mid))
                resIdx = min(cid, resIdx)
                continue
            if contentSoup.body['style']:
                del contentSoup.body['style']
            content = unicode(contentSoup.body).replace(u'<body>', '').replace(u'</body>', '').replace(u'\n\n',
                                                                                                       u'\n').replace(
                u'<br><br>', u'<br>').replace(u'<br\><br\>', u'<br\>')
            capObj['content'] = content
            capObj['title'] = unicode(contentSoup.title.get_text())
            capObj['rawUrl'] = capContentUrl
            # capObj['size'] = int(WordsCount)
            capObj['size'] = len(content)
            capObj['bookId'] = bookObj['id']
            capObj['source'] = bookObj['source']
            capObj['idx'] = cid
            capObj['bookUUID'] = bookObj['digest']

            digest = getCapDigest(bookObj, capObj, cid)

            capObj['digest'] = digest

            befInsertCap = time.time()
            crawlParseSpent = crawlParseSpent + (befInsertCap - befCrawl)

            capId = insertCapWithCapObj(capObj)

            aftInsertCap = time.time()
            insertCap = insertCap + (aftInsertCap - befInsertCap)

            if not capId:
                continue
            upload2Bucket(str(capObj['id']) + '.json', json.dumps(capObj))

            aftUploadCap = time.time()
            uploadCap = uploadCap + (aftUploadCap - aftInsertCap)

        except Exception as e:
            myLogging.error('crawl' + str(mid) + ' cap ' + str(cid) + ' exception: ' + str(e))
            resIdx = min(cid, resIdx)
    if succCapTimes > 1:
        succCapTimes = succCapTimes - 1
    myLogging.info( 'crawlParse avg: ' + str(float(crawlParseSpent) / float(succCapTimes)) + \
        ' insert avg: ' + str(float(insertCap) / float(succCapTimes)) + \
        ' upload avg: ' + str(float(uploadCap) / float(succCapTimes)))
    return resIdx

def getBookObj(allowUpdate, mid):
    befBookObj = time.time()
    bookObj, count = crawlCurrentBookObj(mid)
    aftBookObj = time.time()

    bookObj = insertBookWithConn(bookObj, allowUpdate)
    # aftInsertBookObj = time.time()
    myLogging.info('crawl book spent' + str(aftBookObj - befBookObj) + ' secs; insert spent ' + str(time.time() - aftBookObj))
    return bookObj, count


def crawlCurrentBookObj(mid):
    url = MianFeiTXTBaseUrl + str(mid)
    baseInfoContent = getContentWithUA(url, ua)
    if not baseInfoContent:
        baseInfoContent = getContentWithUA(url, ua)
    baseObj = json.loads(baseInfoContent)
    baseData = baseObj['data']
    author = baseData['author']
    title = baseData['name']
    coverUrl = baseData['coverUrl']
    contentUrl = baseData['contentUrl']
    count = baseData['count'] #不准，更新不及时
    if count < MINCHAPNUM:
        myLogging.warning( 'chapNum too small, skip %s', str(mid))
        # return None, None
    isOver = baseData['isOver']
    BookType = '连载'
    if isOver == 1:
        BookType = '完结'
    bookDetailHtml = getContentWithUA(MianFeiTXTBookDetailUrl + str(mid), ua)
    bookDetailSoup = getSoupByStr(bookDetailHtml)
    bookDesc = bookDetailSoup.select_one('#J-desc').get_text().replace('\n', '').replace('\t\t', '\t')
    bookLabels = []
    for span in bookDetailSoup.select('#J-lables-items span'):
        bookLabels.append(span.get_text())
    bookObj = dict()
    bookObj['subtitle'] = bookDesc
    bookObj['source'] = "" + str(mid)
    bookObj['rawUrl'] = url
    bookObj['title'] = title
    bookObj['chapterNum'] = count #更新不及时
    bookObj['imgUrl'] = coverUrl
    bookObj['author'] = author
    bookObj['size'] = count * 1000
    bookObj['category'] = ''
    if len(bookLabels) > 0:
        bookObj['category'] = bookLabels[0]
    bookObj['type'] = ''
    if len(bookLabels) > 0:
        bookObj['type'] = bookLabels[0]
    if len(bookLabels) > 1:
        bookObj['type'] = bookLabels[1]
    bookObj['bookType'] = BookType
    bookObj['typeCode'] = 0
    bookObj['categoryCode'] = 0
    bookObj['viewNum'] = random.randint(500000, 1000000)

#获取最新章节下标，作为另一个判断更新的条件
    bookObj['latestCapIndex'] = 0
    try:

        capExamples = bookDetailSoup.select('.J-category-li')
        if capExamples and len(capExamples) > 2:
            bookObj['latestCapIndex'] = int(capExamples[2]['id'])#就要第三个，有时候共有3个，有时共有6个

    except Exception  :
        myLogging.warning(traceback.format_exc())

    return bookObj, count


def mianfeiSearch(name, top = 5):
    url = MianFeiTXTSearchBaseUrl + quote(name.encode('utf-8'))
    soup = getSoupByUrl(url)
    bookTags = soup.select_one('#J-items')
    books = []
    for i in range(0, len(bookTags.select('li'))):
        if i > (top - 1): #只取前五个
            break
        bookTag = bookTags.select('li')[i]
        book = dict()
        book['title'] = bookTag.select_one('.title').get_text()
        book['img'] = bookTag.select_one('.img img')['src']
        book['author'] = bookTag.select_one('.author').get_text().replace(' ','').replace('&nbsp;','')
        book['finishwb'] = u'连载'
        if(bookTag.select_one('.finishwb')):
            book['finishwb'] = bookTag.select_one('.finishwb').get_text()

        href = bookTag.select_one('.title')['href']
        index = href.find('id=')
        if index < 0:
            raise InputException('cant find id in mianfeiTXT')
        book['id'] = href[index + 3:].replace(',', '').replace(')','').replace('\\','').replace("'",'')

        books.append(book)

    return books

class MianFeiTXTCrawler(BaseCrawler):

    def init(self, data = None):
        if not data or not isinstance(data, dict):
            raise InputException("requried dict data with fields: sid")
        if not data.has_key('id'):
            raise InputException("requried field 'id' in data")

        self.mid = data['id']

    def crawl(self):
        myLogging.info('mianfeiTXT crawl')
        handleByMTID(self.mid)

    def output(self):
        myLogging.info('mianfeiTXT output')

    def search(self, searchInput, top = 5):
        return  mianfeiSearch(searchInput, top)

# def addGroupMembers():
#     import random
#     count = random.randint(10, 30)
#     for userId in random.sample(range(0, 50), count)

if __name__ == '__main__':
    # handleByMTID(290172)
    # handleByMTID(171117)

    handleByMTID(288443)
    # handleByMTID(183433)
    # handleByMTID(249357)
    # handleByMTID(236565)
    # handleByMTID(87433)

    # for myBookId in (221449, 55255,290172,213005,236565,249357,183433,263175,286271, 293046):
    # for myBookId in (213005,236565,249357,183433,263175,286271, 293046):
    # for myBookId in (286271, 293046):
    #     handleByMTID(myBookId)

    # handleWebsiteNoise(581398, 582410)
    # dealBookComment()

    # import sys
    # handleByMTID(int(sys.argv[1]))
    # dealCommsByBookId(74388, 5820364)
    # uploadCapFromTo(313482, 1200000)
    # uploadCapFromTo(int(sys.argv[1]), int(sys.argv[2]))

    # shuqCategory2 = loadShuQC()

    # start(3980892,shuqCategory2)
    # start(115468,shuqCategory2)
    # from multiprocessing import Pool
    #
    # manager = multiprocessing.Manager()
    #
    # # 父进程创建Queue，并传给各个子进程：
    # queue = manager.Queue(maxsize=100)
    #
    # p = Pool(3)
    #
    # p.apply_async(onlyInsertCap, args=(queue,))
    # p.apply_async(onlyInsertCap, args=(queue,))
    # # p.apply_async(onlyInsertCap, args=(queue,))
    #
    # startFromCId(p,queue)
    # ids = '6692553,4871569,5067938,57392,51602'
    # for bookId in ids.split(','):
    #     start(bookId, shuqCategory2)
    # startFromLatestAjax()
