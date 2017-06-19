##!/usr/bin/python
# -*- coding: UTF-8 -*-
import hashlib
import json
import random
import time
from xml.etree import ElementTree

# def print_node(node):
#     '''''打印结点基本信息'''
#     print "=============================================="
#     print "node.attrib:%s" % node.attrib
#     if node.attrib.has_key("age") > 0 :
#         print "node.attrib['age']:%s" % node.attrib['age']
#     print "node.tag:%s" % node.tag
#     print "node.text:%s" % node.text
import MySQLdb
import yaml

from Config import EADHOST, EADPASSWD, bloomDumpCapsName, MINCHAPNUM
from dao.aliyunOss import upload2Bucket
from dao.connFactory import getDushuConnCsor
from dao.dushuService import getExistsCapsRawUrlId, insertCapWithCapObj2, insertCapWithCapObj, \
    loadExistsSQId, delBookById, insertBookWithConn
from local.shuqi.shuqiLocal import loadShuQSeqC, loadShuQC
from util.UUIDUtils import getBookDigest, getCapDigest
from util.networkHelper import getContent, getContentWithUA
from util.pyBloomHelper import getBloom, loadBloomFromFile, dumpBloomToFile

ua = 'Mozilla/5.0 (Linux; U; Android 4.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, ' \
     'like Gecko) Version/4.0 Safari/534.13'
capListAPIDeviceInfo = '&soft_id=1&ver=110817&platform=an&placeid=1007&imei=862953036746111&cellid=13&lac=-1&sdk=18' \
                       '&wh=720x1280&imsi=460011992901111&msv=3&enc=666501479540451111&sn=1479540459901111&vc=e8f2' \
                       '&mod=M3'

donedegest = getBloom(1500 * 10000)

shuqCategory = loadShuQC()

gBookDict = dict()

# from DBUtils.PooledDB import PooledDB
#
# pool2 = PooledDB(creator=MySQLdb, mincached=1, maxcached=1,
#                 host=EADHOST, port=3306, user="ead",
#                 passwd=EADPASSWD, db="dushu", use_unicode=True, charset='utf8')
# conn2 = pool2.connection()
# csor2 = conn2.cursor()
#
# # conn.set_character_set('utf8')
# csor2.execute('SET NAMES utf8')
# csor2.execute("SET CHARACTER SET utf8")
# csor2.execute("SET character_set_connection=utf8")

def initCap():
    sqCat = dict()
    for i in range(0,800):
        url = 'http://api.shuqireader.com/reader/bc_storylist.php?pagesize=40&PageType=category&item=allclick' \
              '&pageIndex=1&cid=' \
              + str(i) + capListAPIDeviceInfo
        text = getContentWithUA(url, ua)

        if not (text and len(text) > 60 ):
            continue

        root = ElementTree.fromstring(text.encode('utf-8'))

    # 获取element的方法
    # 1 通过getiterator
        node = root.getiterator("Book")[0]

        parentName = node.attrib['ParentTypeName']
        ParentTypeId = node.attrib['ParentTypeId']
        TypeName = node.attrib['TypeName']

        print TypeName,ParentTypeId, parentName

        tag = dict()
        tag['TypeName'] = TypeName
        # tag['parentName'] = parentName
        # tag['ParentTypeId'] = ParentTypeId
        tag['cid'] = i

        if not sqCat.has_key(parentName):

            chidren = []
            chidren.append(tag)
            top = dict()
            top['id'] = ParentTypeId
            top['children'] = chidren
            sqCat[parentName] = top
        else:
            sqCat[parentName]['children'].append(tag)
        # sqCat[i] = tag

    f = open('shuqCategory.yaml', 'wb')
    yaml.dump(sqCat, f)
    f.close()

    # for node in lst_node:
    #     print_node(node)
    #
    #     # 2通过 getchildren
    # lst_node_child = lst_node[0].getchildren()[0]
    # print_node(lst_node_child)
    #
    # # 3 .find方法
    # node_find = root.find('person')
    # print_node(node_find)
    #
    # # 4. findall方法
    # node_findall = root.findall("person/name")[1]
    # print_node(node_findall)

def sizeStr2Int(size):
    size = size.strip()
    carryName = size[-1:]
    carry = 1000
    if carryName == u'万':
        carry = 10000
    elif carryName == u'千':
        carry = 1000
    count = 1
    try:
        # count = float(carryName[0: -1])
        countStr = size[0: -1]
        import ast
        count = ast.literal_eval(countStr)
    except Exception as e:
        print '计算书的大小出错',e
    return int(carry * count)

def handleOneBook(id,shuqCategory):

    # shuqCategory = loadShuQC()

    bookObj, digest = getBookObjFromSQid(id, shuqCategory)

    if not bookObj or not digest:
        return None
    global gBookDict
    if gBookDict.has_key(digest):
        albook = gBookDict[digest]
        # if (not albook['bookType'] or albook['bookType'] == u'完结') and albook['doneCount'] >= albook['chapterNum']:
        bookObj['id'] = albook['id']
        print 'book exists, ',bookObj['title']
        return bookObj
        # return None
    gBookDict[digest] = bookObj


    bookObj = insertBookWithConn(bookObj)

    return bookObj

    # existsCaps = getExistsCaps(bookObj['id'])


def getBookObjFromSQid(id, shuqCategory):
    bookInfoAPI = 'http://api.shuqireader.com/reader/bc_cover.php?bookId=' + str(
        id) + '&book=same&book_num=5&bbs=pinglun&bbs_num=8&bbs_rand_num=1&lastchaps=1&ItemCount=3' \
              '&soft_id=1&ver=110817&platform=an&placeid=1007&imei=862953036746111&cellid=13&lac=-1' \
              '&sdk=18&wh=720x1280&imsi=460011992901111&msv=3&enc=666501479540451111&sn=1479540459901111&vc=e8f2&mod=M3'
    text = getContent(bookInfoAPI)
    if not (text and len(text) > 160):
        return None,None
    root = ElementTree.fromstring(text.encode('utf-8'))
    BookType = ''
    if len(root.getiterator('BookType')) > 0:
        BookType = root.getiterator('BookType')[0].text
    category = ''
    if len(root.getiterator('NickName')) > 0:
        category = root.getiterator('NickName')[0].text
    tag = ''
    if len(root.getiterator('ShortNickName')) > 0:
        tag = root.getiterator('ShortNickName')[0].text
    tagId = 0
    if root.getiterator('NickId') and len(root.getiterator('NickId')) > 0 and root.getiterator('NickId')[0].text:
        tagId = int(root.getiterator('NickId')[0].text)
    firstCid = 0
    if root.getiterator('ChapteridFirst') and len(root.getiterator('ChapteridFirst')) > 0 \
            and root.getiterator('ChapteridFirst')[0].text:
        firstCid = int(root.getiterator('ChapteridFirst')[0].text)

    if (not BookType) and (not category) and (not tag) and (not tagId):
        return None,None
    categoryId = 0
    if shuqCategory.has_key(tag):
        if shuqCategory[tag]['id'] and len(shuqCategory[tag]['id']) > 0:
            categoryId = int(shuqCategory[tag]['id'])
    size = 1
    if root.getiterator('Size') and len(root.getiterator('Size')) > 0:
        strSize = root.getiterator('Size')[0].text
        size = sizeStr2Int(strSize)
    NumChapter = 1
    if root.getiterator('NumChapter') and len(root.getiterator('NumChapter')) > 0 and root.getiterator('NumChapter')[0].text:
        NumChapter = int(root.getiterator('NumChapter')[0].text)

    if NumChapter < MINCHAPNUM:
        return None,None
    source = 'shuqi' + str(id)
    subtitle = root.getiterator('Description')[0].text
    title = root.getiterator('BookName')[0].text
    author = root.getiterator('Author')[0].text
    imgurl = root.getiterator('ImageExists')[0].text
    certainBookUrl = 'http://api.shuqireader.com/reader/bc_cover.php?bookId=' + str(id)
    if not title or len(title) < 1 or len(author) < 1:
        return None,None
    bookObj = dict()
    bookObj['subtitle'] = subtitle
    bookObj['source'] = source
    bookObj['rawUrl'] = certainBookUrl
    bookObj['title'] = title
    bookObj['chapterNum'] = NumChapter
    bookObj['imgUrl'] = imgurl
    bookObj['author'] = author
    bookObj['size'] = size
    bookObj['category'] = tag
    bookObj['type'] = category
    bookObj['bookType'] = BookType
    # bookObj['typeCode'] = 100 + tagId
    # bookObj['categoryCode'] = 100 + categoryId
    bookObj['typeCode'] = tagId
    bookObj['categoryCode'] = categoryId
    bookObj['firstCid'] = firstCid
    bookObj['viewNum'] = 0

    digest = getBookDigest(author, title)
    bookObj['digest'] = digest
    return bookObj, digest


def getShuqiCapList(bookId):

    capList = []

    pageIndex = 1
    capListAPIBase = 'http://api.shuqireader.com/reader/bc_chapter.php?pagesize=40&bookId='

    capListAPI = capListAPIBase + str(bookId) + '&pageIndex=' + str(pageIndex) + capListAPIDeviceInfo

    text = getContentWithUA(capListAPI, ua)

    if not (text and len(text) > 160):
        return

    root = ElementTree.fromstring(text.encode('utf-8'))

    gatherId = root.getiterator('BookInfos')[0].attrib['GatherId']
    TotalCount = int(root.getiterator('BookInfos')[0].attrib['TotalCount'])
    # if TotalCount > 40:
    topPageCount = TotalCount / 40 + 2#分页的总数
    for i in range(1, topPageCount):#如果没有分页，i只会等于1
        if i == 1:
            pageRoot = root
        else:
            pageApi = capListAPIBase + str(bookId) + '&pageIndex=' + str(i) + capListAPIDeviceInfo
            pageText = getContentWithUA(pageApi, ua)

            if not (pageText and len(pageText) > 160):
                return
            pageRoot = ElementTree.fromstring(pageText.encode('utf-8'))

        if gatherId and gatherId != '':#有子目录
            for book in pageRoot.getiterator('Book'):
                vId = book.attrib['ChapterId']

                secondApi = capListAPI + '&vid=' + str(vId)#子目录的url
                textSon = getContentWithUA(secondApi, ua)#子目录的内容

                xmlSon = ElementTree.fromstring(textSon.encode('utf-8')) #子目录的xml

                sonTotalCount = int(xmlSon.getiterator('BookInfos')[0].attrib['TotalCount']) #子目录的记录总数
                sonPageCount = sonTotalCount / 40 + 2#子目录的分页总数
                for j in range(1, sonPageCount):#遍历子目录的每一页，如果没有分页，会只遍历第一页
                    if j == 1:
                        sonpageRoot = xmlSon#第一页不需要再请求url
                    else:
                        morePageApi = capListAPIBase + str(bookId) + '&pageIndex=' + str(j) + capListAPIDeviceInfo \
                                  + '&vid=' + str(vId)#子目录的分页url
                        morePageText = getContentWithUA(morePageApi, ua)
                        sonpageRoot = ElementTree.fromstring(morePageText.encode('utf-8'))  # 子目录的xml

                    for realCap in sonpageRoot.getiterator('Book'):
                        realCapId = realCap.attrib['ChapterId']
                        # dealCap(bookId, realCapId)
                        capList.append(realCapId)

        else:#没有二级目录，不需要请求信的api，所有不需考虑分页
            for realCap in pageRoot.getiterator('Book'):
                realCapId = realCap.attrib['ChapterId']
                # dealCap(bookId, realCapId)
                capList.append(realCapId)

    return capList


def getCapContentObj(bookId, capId,mysqlBKid):
    pageIndex = 1
    capListAPIBase = 'http://api.shuqireader.com/reader/bc_showchapter.php?bookId='

    capApi = capListAPIBase + str(bookId) + '&chapterid=' + str(capId) + '&pageIndex=' + str(pageIndex) \
             + '&bg=0' + capListAPIDeviceInfo
    capText = getContentWithUA(capApi, ua)

    if not (capText and len(capText) > 30):
        print 'cap content too short ,skip and del book'
        # delBookById(mysqlBKid)
        return None
    capRoot = ElementTree.fromstring(capText.encode('utf-8'))

    ChapterName = ''
    if len(capRoot.getiterator('ChapterName')) > 0:
        ChapterName = capRoot.getiterator('ChapterName')[0].text

    ChapterContent = ''
    if len(capRoot.getiterator('ChapterContent')) > 0:
        ChapterContent = capRoot.getiterator('ChapterContent')[0].text
    if not ChapterContent:
        capText = getContentWithUA(capApi, ua)

        if not (capText and len(capText) > 30):
            print 'cap content too short ,skip and del book'
            delBookById(mysqlBKid)
            return None
        capRoot = ElementTree.fromstring(capText.encode('utf-8'))

        ChapterName = ''
        if len(capRoot.getiterator('ChapterName')) > 0:
            ChapterName = capRoot.getiterator('ChapterName')[0].text

        ChapterContent = ''
        if len(capRoot.getiterator('ChapterContent')) > 0:
            ChapterContent = capRoot.getiterator('ChapterContent')[0].text
    if not ChapterContent:
        return None
    ChapterContent = ChapterContent.strip()

    if(ChapterContent.startswith('http') and len(ChapterContent) < 250):
        print 'cap content is url ,skip and del book', bookId, ' : ',ChapterContent
        delBookById(mysqlBKid)
        return None
    WordsCount = ''
    if len(capRoot.getiterator('WordsCount')) > 0:
        WordsCount = capRoot.getiterator('WordsCount')[0].text

    PageCount = 1
    if len(capRoot.getiterator('PageCount')) > 0:
        PageCount = int(capRoot.getiterator('PageCount')[0].text)
    if PageCount > 1:
        for i in range(2, PageCount + 1):
            pageIndex = i
            capApi2 = capListAPIBase + str(bookId) + '&chapterid=' + str(capId) + '&pageIndex=' + str(
                pageIndex) + '&bg=0' + capListAPIDeviceInfo
            capText2 = getContentWithUA(capApi2, ua)

            if not (capText2 and len(capText2) > 160):
                return
            capRoot2 = ElementTree.fromstring(capText2.encode('utf-8'))
            ChapterContent2 = ''
            if len(capRoot2.getiterator('ChapterContent')) > 0:
                ChapterContent2 = capRoot2.getiterator('ChapterContent')[0].text
            ChapterContent = ChapterContent + ChapterContent2

    capObj = dict()
    capObj['content'] = ChapterContent.replace(u'***求收藏***','').replace(u'***（求收藏）***','').replace(u'求收藏','')
    capObj['title'] = ChapterName
    capObj['rawUrl'] = capApi[0:200]
    # capObj['size'] = int(WordsCount)
    capObj['size'] = len(capObj['content'])
    return capObj


# def dealCap(bookId, capId):
#     capObj = getCapContentObj(bookId, capId)
#     insertCapWithCapObj(capObj)

# def getCapObjListByBookId(bookId):





def start(bookId, shuqCategory2 = None):


    if not shuqCategory2:
        global shuqCategory
        shuqCategory2 = shuqCategory

    global donedegest
    capObjList = getCapObjListByBookId(bookId, shuqCategory2)
    if not capObjList:
        print 'no capObjList, ',bookId
        return
    for capObj in capObjList:
        capId = insertCapWithCapObj2(capObj)
        donedegest.add(capObj['digest'])

        if not capId:
            continue
        upload2Bucket(str(capObj['id']) + '.json', json.dumps(capObj))
    # existsCaps = getExistsCaps(bookObj['id'])


def getCapObjListByBookId(bookId,shuqCategory2):

    bookObj = handleOneBook(bookId,shuqCategory2)
    if (not bookObj ) or not  bookObj.has_key('id'):
        print 'book null', bookId
        return
    capList = getShuqiCapList(bookId)
    capObjList = []
    global donedegest
    for j in range(0, len(capList)):
        capId = capList[j]
        capObj = getCapContentObj(bookId, capId, bookObj['id'])
        if not capObj:
            return
        capObj['bookId'] = bookObj['id']
        capObj['source'] = bookObj['source']
        capObj['idx'] = j
        capObj['bookUUID'] = bookObj['digest']

        digest = getCapDigest(bookObj, capObj, j)
        capObj['digest'] = digest

        if digest in donedegest:
            continue
        capObjList.append(capObj)
        # tt = random.randint(1,3)
        # time.sleep(tt)
    return capObjList


def getCapObjListByBookIdIntoQue(bookId, queue, categoryDict, connDoc,csorDoc):
    bookObj = handleOneBook(bookId,categoryDict, connDoc,csorDoc)
    if (not bookObj or not bookId ) or not  bookObj.has_key('id'):
        return
    capList = getShuqiCapList(bookId)
    # capObjList = []
    for j in range(0, len(capList)):
        capId = capList[j]
        capObj = getCapContentObj(bookId, capId,bookObj['id'])
        if not capObj:
            return
        capObj['bookId'] = bookObj['id']
        capObj['source'] = bookObj['source']
        capObj['idx'] = j
        capObj['bookUUID'] = bookObj['digest']

        digest = getCapDigest(bookObj, capObj, j)

        capObj['digest'] = digest
        if digest in donedegest:
            return
        # capObjList.append(capObj)
        # for capObj in capObjList:
        # print 'queue size: ', len(queue)
        queue.put(capObj)


def startFromLatestAjax():
    baseUrl = 'http://ajax.shuqiapi.com/?bamp=sqphcm&desc_type=3&page='
    tailUrl = '&tk=NDE3YWM1OWU5Zg%253D%253D'
    page = 1
    import json
    for page in range(86, 120):
        url = baseUrl + str(page) + tailUrl

        jsonContent = getContentWithUA(url,ua)
        jsonC = json.loads(jsonContent.encode('utf-8'))

        for book in jsonC['data']['ph']['book_list']:
            bookId = book['id']
            try:
                start(bookId)
            except Exception as e:
                print 'book ',bookId,' error: ', e

def startFromCId(p, queue):
    baseUrl = 'http://api.shuqireader.com/reader/bc_storylist.php?pagesize=40&PageType=category&item=allclick&pageIndex='
    cc = '&cid='
    page = 1
    shuqCategory = loadShuQSeqC()
    shuqCategory2 = loadShuQC()
    totleSize = 220



    for cid in shuqCategory.keys():

        try:

            url = baseUrl + str(page) + cc + str(cid) + capListAPIDeviceInfo

            urlContent = getContentWithUA(url, ua)

            if not (urlContent and len(urlContent) > 30):
                continue

            capRoot = ElementTree.fromstring(urlContent.encode('utf-8'))

            totleSize = int(capRoot.attrib['TotalCount']) / 40 + 1

            try:
                dealBookListUrlContentMT(p, queue, shuqCategory2, urlContent)

                for page in range(totleSize, 0, -1):
                    url = baseUrl + str(page) + cc + str(cid) + capListAPIDeviceInfo

                    urlContent = getContentWithUA(url,ua)

                    if not (urlContent and len(urlContent) > 30):
                        continue

                    dealBookListUrlContentMT(p, queue, shuqCategory2, urlContent)
            except Exception as e1:
                print 'deal one page error, cid: ',cid,' page: ' ,page
        except Exception as e:
            print "cid : ", cid, 'error: ',e

def startFromCId():
    baseUrl = 'http://api.shuqireader.com/reader/bc_storylist.php?pagesize=40&PageType=category&item=allclick&pageIndex='
    cc = '&cid='
    page = 1
    shuqCategory = loadShuQSeqC()
    # shuqCategory2 = loadShuQC()
    # totleSize = 220



    for cid in shuqCategory.keys():

        try:

            url = baseUrl + str(page) + cc + str(cid) + capListAPIDeviceInfo

            urlContent = getContentWithUA(url, ua)

            if not (urlContent and len(urlContent) > 30):
                continue

            capRoot = ElementTree.fromstring(urlContent.encode('utf-8'))

            totleSize = int(capRoot.attrib['TotalCount']) / 40 + 1

            try:
                dealBookListPrintBooks(urlContent)

                for page in range(totleSize, 0, -1):
                    url = baseUrl + str(page) + cc + str(cid) + capListAPIDeviceInfo

                    urlContent = getContentWithUA(url,ua)

                    if not (urlContent and len(urlContent) > 30):
                        continue

                    dealBookListPrintBooks( urlContent)
            except Exception as e1:
                print 'deal one page error, cid: ',cid,' page: ' ,page
        except Exception as e:
            print "cid : ", cid, 'error: ',e

def dealBookListPrintBooks( urlContent):
    capRoot = ElementTree.fromstring(urlContent.encode('utf-8'))
    if len(capRoot.getiterator('Book')) > 0:
        for book in capRoot.getiterator('Book'):
            bookId = book.attrib['BookId']
            global donedegest
            if not 'http://api.shuqireader.com/reader/bc_cover.php?bookId=' + bookId in donedegest:
                print bookId
        # p.apply_async(startByXmlDoc, args=(capRoot, queue, shuqCategory2))
        # time.sleep(5)

def dealBookListUrlContentMT(p, queue, shuqCategory2, urlContent):
    capRoot = ElementTree.fromstring(urlContent.encode('utf-8'))
    if len(capRoot.getiterator('Book')) > 0:
        p.apply_async(startByXmlDoc, args=(capRoot, queue, shuqCategory2))
        time.sleep(5)


def startByXmlDoc(capRoot, queue,shuqCategory2):
    # shuqCategory2 = loadShuQC()

    from DBUtils.PooledDB import PooledDB

    poolDoc = PooledDB(creator=MySQLdb, mincached=1, maxcached=3,
                     host=EADHOST, port=3306, user="ead",
                     passwd=EADPASSWD, db="dushu", use_unicode=True, charset='utf8')
    connDoc = poolDoc.connection()
    csorDoc = connDoc.cursor()

    # conn.set_character_set('utf8')
    csorDoc.execute('SET NAMES utf8')
    csorDoc.execute("SET CHARACTER SET utf8")
    csorDoc.execute("SET character_set_connection=utf8")

    for book in capRoot.getiterator('Book'):
        bookId = book.attrib['BookId']
        try:
            getCapObjListByBookIdIntoQue(bookId, queue,shuqCategory2, connDoc,csorDoc)
        except Exception as e:
            print 'bookId: ', bookId, e
        # capObjList = getCapObjListByBookId(bookId)
        # for capObj in capObjList:
        #     queue.put(capObj)



def getContentFromXml(bookId, capId, xml):
    pageIndex = 1
    capListAPIBase = 'http://api.shuqireader.com/reader/bc_showchapter.php?bookId='

    # capApi = capListAPIBase + str(bookId) + '&chapterid=' + str(capId) + '&pageIndex=' + str(
    #     pageIndex) + '&bg=0' + capListAPIDeviceInfo
    # capText = getContentWithUA(capApi, ua)

    # if not (capText and len(capText) > 30):
    #     print 'cap content too short ,skip and del book'
    #     delBookById(bookId)
    #     return None
    capRoot = ElementTree.fromstring(xml.encode('utf-8'))

    # ChapterName = ''
    # if len(capRoot.getiterator('ChapterName')) > 0:
    #     ChapterName = capRoot.getiterator('ChapterName')[0].text

    ChapterContent = ''
    if len(capRoot.getiterator('ChapterContent')) > 0:
        ChapterContent = capRoot.getiterator('ChapterContent')[0].text

    # if ('http://' in ChapterContent and len(ChapterContent) < 250):
    #     print 'cap content is url ,skip and del book', bookId, ' : ', ChapterContent
    #     delBookById(bookId)
    #     return None
    WordsCount = ''
    # if len(capRoot.getiterator('WordsCount')) > 0:
    #     WordsCount = capRoot.getiterator('WordsCount')[0].text

    PageCount = 1
    if len(capRoot.getiterator('PageCount')) > 0:
        PageCount = int(capRoot.getiterator('PageCount')[0].text)
    if PageCount > 1:
        for i in range(2, PageCount + 1):
            pageIndex = i
            capApi2 = capListAPIBase + str(bookId) + '&chapterid=' + str(capId) + '&pageIndex=' + str(
                pageIndex) + '&bg=0' + capListAPIDeviceInfo
            capText2 = getContentWithUA(capApi2, ua)

            if not (capText2 and len(capText2) > 160):
                return
            capRoot2 = ElementTree.fromstring(capText2.encode('utf-8'))
            ChapterContent2 = ''
            if len(capRoot2.getiterator('ChapterContent')) > 0:
                ChapterContent2 = capRoot2.getiterator('ChapterContent')[0].text
            ChapterContent = ChapterContent + ChapterContent2

    return ChapterContent

def getContentByUrl(url):
    capText = getContentWithUA(url, ua)

    if not (capText and len(capText) > 30):
        print 'cap content too short ,skip and del book'
        return None
    capRoot = ElementTree.fromstring(capText.encode('utf-8'))

    # ChapterName = ''
    # if len(capRoot.getiterator('ChapterName')) > 0:
    #     ChapterName = capRoot.getiterator('ChapterName')[0].text

    ChapterContent = ''
    if len(capRoot.getiterator('ChapterContent')) > 0:
        ChapterContent = capRoot.getiterator('ChapterContent')[0].text

    # if ('http://' in ChapterContent and len(ChapterContent) < 250):
    #     print 'cap content is url ,skip and del book', bookId, ' : ', ChapterContent
    #     delBookById(bookId)
    #     return None
    WordsCount = ''
    # if len(capRoot.getiterator('WordsCount')) > 0:
    #     WordsCount = capRoot.getiterator('WordsCount')[0].text

    PageCount = 1
    if len(capRoot.getiterator('PageCount')) > 0:
        PageCount = int(capRoot.getiterator('PageCount')[0].text)
    if PageCount > 1:
        for i in range(2, PageCount + 1):
            pageIndex = i
            capApi2 = url.replace('pageIndex=' + str(pageIndex - 1),'pageIndex=' + str(pageIndex - 1))#capListAPIBase + str(bookId) + '&chapterid=' + str(capId) + '&pageIndex=' + str(
                # pageIndex) + '&bg=0' + capListAPIDeviceInfo
            capText2 = getContentWithUA(capApi2, ua)

            if not (capText2 and len(capText2) > 160):
                return
            capRoot2 = ElementTree.fromstring(capText2.encode('utf-8'))
            ChapterContent2 = ''
            if len(capRoot2.getiterator('ChapterContent')) > 0:
                ChapterContent2 = capRoot2.getiterator('ChapterContent')[0].text
            if ChapterContent == ChapterContent2:
                break
            ChapterContent = ChapterContent + ChapterContent2
    return ChapterContent

def shuqiUpdateFromRawUrl():
    ids = '53802'
    for id in ids.split(','):
        res = getExistsCapsRawUrlId(int(id))
        for cap in res:
            cid = cap[0]
            url = cap[1]
            if not url or len(url) < 1:
                print cid, 'no url, skip'
                break

            # content,host = getAndParse(url)
            # updateContentById(cid, content)






def onlyInsertCap(queue):
    from DBUtils.PooledDB import PooledDB

    pool3 = PooledDB(creator=MySQLdb, mincached=1, maxcached=2,
                    host=EADHOST, port=3306, user="ead",
                    passwd=EADPASSWD, db="dushu", use_unicode=True, charset='utf8')
    conn3 = pool3.connection()
    csor3 = conn3.cursor()

    # conn.set_character_set('utf8')
    csor3.execute('SET NAMES utf8')
    csor3.execute("SET CHARACTER SET utf8")
    csor3.execute("SET character_set_connection=utf8")


    while True:
        capObj = queue.get()
        # print i, capObj['source'] + capObj['idx']
        try:
            capId = insertCapWithCapObj(capObj, conn3, csor3)
            if not capId:
                continue
            upload2Bucket(str(capObj['id']) + '.json', json.dumps(capObj))
            global donedegest
            donedegest.add(capObj['digest'])
        except Exception as e:
            print 'insertCap error, ', e


def shuqiAddInitTmp():
    conn2,csor2 = getDushuConnCsor()

    csor2.execute("select rawUrl from cn_dushu_book")
    conn2.commit()
    # bookDict = dict()
    res = csor2.fetchall()
    for book in res:
        source = book[0]
        global donedegest
        donedegest.add(source)

    csor2.close()
    conn2.close()



def shuqiAddInit():
    global gBookDict
    gBookDict = loadExistsSQId()

    conn2,csor2 = getDushuConnCsor()

    global donedegest
    donedegest = loadBloomFromFile(bloomDumpCapsName)
    if donedegest:
        print 'load bloom from file succ, no need load from db'
        return
    else:
        print 'load from db'
        donedegest  = getBloom(2000 * 10000)


    csor2.execute("select id from cn_dushu_acticle order by id desc limit 1")
    conn2.commit()
    length = csor2.fetchone()[0]
    step = 0
    carry = 500000
    # while step < length - 1500000:
    while step < length :

        csor2.execute("select digest from cn_dushu_acticle where id > %s and id < %s", (step, step + carry))
        conn2.commit()
        step = step + carry
        caps = csor2.fetchall()

        for cap in caps:
            digest = cap[0]
            # bookDigest = cap[1]
            # beg = time.time()
            # if not bookDigest in bookDict.keys():
            #     dictTook = time.time()
            #     print 'dict took: ', dictTook - beg
            #     continue
            # dictTook = time.time()
            # print 'dict took: ',dictTook - beg
            donedegest.add(digest)

            # blTook = time.time()
            # print 'bl took: ',blTook - dictTook
    # global gBookDict
    # gBookDict =  bookDict
    dumpBloomToFile(donedegest, bloomDumpCapsName)

    csor2.close()
    conn2.close()
    return donedegest






if __name__ == '__main__':
    # updateCapDigest()
    # http: // api.shuqireader.com / reader / bc_cover.php?bookId = 93511
    # handleWebsiteNoise(581398, 582410)
    import sys

    bloom = loadExistsSQId()

    shuqCategory2 = loadShuQC()

    st = 10000
    end = 7000000
    if len(sys.argv) > 1:
        st = int(sys.argv[1])
        end = int(sys.argv[2])

    if len(sys.argv) > 3:
        db_dushu = sys.argv[3]
        db_acticle = sys.argv[4]

    shuqiAddInit()

    # nullBookIds = open('nullSQID.txt', 'r')
    # nullIdSet = set()
    # while 1:
    #     sqid = nullBookIds.readline()
    #     if not sqid:
    #         break
    #     nullIdSet.add(int(sqid.replace('\n', '')))

    # st = 10000
    # end = 30000
    # uploadCapByCid(int(sys.argv[1]))

    # uploadCapFromTo(649943, 650090)

    # uploadCapFromTo(int(sys.argv[1]), int(sys.argv[2]))

    # seq = range(st, end)
    print 'start from shuqi id ',st, ' to ',end, '; insert into ', db_dushu ,', and ',db_acticle
    idx = st
    carry = 10000

    while idx < end:
    # seq = range(5000, 6000)
        seq = range(idx, idx + carry)

        random.shuffle(seq)
        #
        for sqBid in seq:
            # print sqBid
            # if sqBid in nullIdSet:
            #     continue
            if not 'shuqi' + str(sqBid) in bloom:
                try:
                    start(3648845,shuqCategory2)
                except Exception as e:
                    print sqBid, ':  ',e
                except IOError as e2:
                    print sqBid, ':  ',e2
                bloom.add('shuqi' + str(sqBid))

        idx = idx + carry
        # dumpBloomToFile(donedegest)

    # start(5837744, shuqCategory2)


    # start(115468,shuqCategory2)

    # shuqiAddInitTmp()
    # startFromCId()
    # shuqiAddInit()
    # miss = open('missBookId.txt', 'r')
    # while 1:
    #     line = miss.readline()
    #     if not line:
    #         break
    #     lineArr = line.split(',')
    #     bookId = lineArr[0]
    #     csor2.execute('select rawUrl from cn_dushu_book where id = %s', (bookId,))
    #     conn2.commit()
    #     rawUrl = csor2.fetchone()[0]
    #     findex = rawUrl.find('bookId=') + 7
    #     if len(rawUrl) - findex > 7:
    #         print bookId
    #         continue
    #     shuqiId = rawUrl[findex:]
    #     start(shuqiId, shuqCategory2)
    # f = open('shuqiBookId.log', 'r')
    # f.readline()
    # while 1:
    #     id = f.readline()
    #     if not id:
    #         break
    #     id = id.replace('\n', '')
    #     start(id, shuqCategory2)



    # from multiprocessing import Pool
    #
    # manager = multiprocessing.Manager()
    #
    # # 父进程创建Queue，并传给各个子进程：
    # queue = manager.Queue(maxsize=100)
    #
    # p = Pool(5)
    #
    # p.apply_async(onlyInsertCap, args=(queue,))
    # # p.apply_async(onlyInsertCap, args=(queue,))
    # # p.apply_async(onlyInsertCap, args=(queue,))
    # #
    # startFromCId(p,queue)
    # p.close()
    # p.join()




    # ids = '6692553,4871569,5067938,57392,51602'
    # for bookId in ids.split(','):
    #     start(bookId, shuqCategory2)
    # startFromLatestAjax()
