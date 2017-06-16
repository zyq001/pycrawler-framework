#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random

from app.ershoufang import Ershoufang
from app.shuqi import start
from dao.dushuService import loadExistsSQId
from local.shuqi.shuqiLocal import loadShuQC
from manager.Manager import Manager, crawlManager
from rest.restServices import WebServer


def shuqiTest():
    # updateCapDigest()
    # http: // api.shuqireader.com / reader / bc_cover.php?bookId = 93511
    # handleWebsiteNoise(581398, 582410)
    import sys

    bloom = loadExistsSQId()

    shuqCategory2 = loadShuQC()

    db_dushu = 'default'
    db_acticle = 'default'

    st = 10000
    end = 7000000
    if len(sys.argv) > 1:
        st = int(sys.argv[1])
        end = int(sys.argv[2])

    if len(sys.argv) > 3:
        db_dushu = sys.argv[3]
        db_acticle = sys.argv[4]

    # 加载已入库的章节digest
    # shuqiAddInit()


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
    print 'start from shuqi id ', st, ' to ', end, '; insert into ', db_dushu, ', and ', db_acticle
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
                    start(3648845, shuqCategory2)
                except Exception as e:
                    print sqBid, ':  ', e
                except IOError as e2:
                    print sqBid, ':  ', e2
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


if __name__ == '__main__':
    crawlManager.crawlers['ershoufang'] = Ershoufang()
    webApp = WebServer()
    webApp.run(port=10008)
    # manager = Manager()
    #
    # ershoufangCrawler = Ershoufang()
    # manager.addCrawler(ershoufangCrawler)
    #
    # manager.start()