#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
抓取北京建委公布成交数据，因为每天只公布前一天的数据，历史数据五处查，自己保存自己分析吧

@author: zyq
'''
from Config import ERSHOUFANGREVEIVER_
from app.baseCrawler import BaseCrawler
from dao.connFactory import getDushuConnCsor
from dao.ershoufangService import getChartAsStr, getImgTag
from util.emailHelper import send_email
from util.htmlHelper import getSoupByStr
from util.networkHelper import getContent
from util.numUtil import str2intNoDot
from util.timeHelper import getToday


class Ershoufang(BaseCrawler):



    def init(self, data = None):
        print 'ershoufang init'

    def output(self):
        print 'ershoufang output'

    def crawl(self):
        try:
            htmlContent = getContent('http://www.bjjs.gov.cn/bjjs/fwgl/fdcjy/fwjy/index.shtml')
            soup = getSoupByStr(htmlContent)
            section = soup.select('.portlet')[1]
            terms = section.select("table[bgcolor='#ffffff']")

            assert len(terms) == 4

            keshou = terms[0]
            tds = keshou.select('td')
            keshou_count = str2intNoDot(tds[2].text.replace(' ', '').replace('\n', ''))
            keshou_area = str2intNoDot(tds[4].text.replace(' ', '').replace('\n', ''))
            keshou_zhuzai_count = str2intNoDot(tds[6].text.replace(' ', '').replace('\n', ''))
            keshou_zhuzai_area = str2intNoDot(tds[8].text.replace(' ', '').replace('\n', ''))

            new_publish = terms[1]
            tds = new_publish.select('td')
            new_publish_count = str2intNoDot(tds[2].text.replace(' ', '').replace('\n', ''))
            new_publish_area = str2intNoDot(tds[4].text.replace(' ', '').replace('\n', ''))
            new_publish_zhuzai_count = str2intNoDot(tds[6].text.replace(' ', '').replace('\n', ''))
            new_publish_zhuzai_area = str2intNoDot(tds[8].text.replace(' ', '').replace('\n', ''))

            sign = terms[3]
            tds = sign.select('td')
            sign_count = str2intNoDot(tds[2].text.replace(' ', '').replace('\n', ''))
            sign_area = str2intNoDot(tds[4].text.replace(' ', '').replace('\n', ''))
            sign_zhuzai_count = str2intNoDot(tds[6].text.replace(' ', '').replace('\n', ''))
            sign_zhuzai_area = str2intNoDot(tds[8].text.replace(' ', '').replace('\n', ''))

            conn, csor = getDushuConnCsor()

            csor.execute("insert cn_test (keshou_count, keshou_area, keshou_zhuzai_count, keshou_zhuzai_area"
                         ", new_publish_count, new_publish_area, new_publish_zhuzai_count, new_publish_zhuzai_area"
                         ", sign_count, sign_area, sign_zhuzai_count, sign_zhuzai_area,src, updateTime)"
                         "value (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                         (keshou_count, keshou_area, keshou_zhuzai_count, keshou_zhuzai_area
                          , new_publish_count, new_publish_area, new_publish_zhuzai_count, new_publish_zhuzai_area
                          , sign_count, sign_area, sign_zhuzai_count, sign_zhuzai_area, htmlContent
                          , unicode(tds[0].text.replace(' ', '').replace('\n', '').replace(u'存量房网上签约', ''))))
            conn.commit()
            print id, ' succ today sign count: ', str(sign_count)

            csor.close()
            conn.close()

            print unicode(tds[0].text.replace(' ', '').replace('\n', '').replace(u'存量房网上签约', ''))

            send_email(msg=unicode(section) + getImgTag(),
                       subject=unicode(tds[0].text.replace(' ', '').replace('\n', '').replace(u'存量房网上签约', ''))
                               + u'网签住宅' + unicode(sign_zhuzai_count) + u'套, 平均'
                               + unicode(float(sign_zhuzai_area) / float(sign_zhuzai_count))
                               + u'平/套'
                       , receivers=ERSHOUFANGREVEIVER_, )



        except Exception as e:
            print 'error:', e
            send_email(msg=unicode(e), subject=u'房产交易抓取异常' + str(getToday()), recievers=['467959945@qq.com'], )

        except AssertionError as e:
            print 'error:', e
            send_email(msg=unicode(e), subject=u'房产交易抓取异常' + str(getToday()), recievers=['467959945@qq.com'], )


# if __name__ == '__main__':

