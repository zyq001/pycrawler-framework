#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import smtplib
import time
from email.header import Header
from email.mime.text import MIMEText

import requests

from Config import MAILPASS, NO_REPLY_TATATIMES_COM, SMTP_EXMAIL_QQ_COM, MANAGER_TATATIMES_COM, \
    NOREPLAYEMAIL, dushuDailyReportReciever

from dao.dushuService import getBookCount, getOnlineBookCount, getCountDuring

yesteday = time.strftime('%Y%m%d', time.localtime(time.time() - 24 * 3600))
# yesteday = time.strftime('%Y%m%d', time.localtime(time.time()))


def dushuDailyReport():
    totleCount = getBookCount()
    onlineCount = getOnlineBookCount()
    nowTime = int(time.time())
    yestedayTime = nowTime - 24*3600
    updateCount = getCountDuring(yestedayTime, nowTime)

    searchTopUrl = 'http://123.56.66.33:19200/log/_search'
    countInput = '''
    {
  "query": {
    "filtered": {
      "query": {
        "query_string": {
          "query": "*",
          "analyze_wildcard": true
        }
      },
      "filter": {
        "bool": {
          "must": [
            {
              "range": {
                "timestamp": {
                  "gte": %s,
                  "lte": %s,
                  "format": "epoch_millis"
                }
              }
            }
          ],
          "must_not": []
        }
      }
    }
  },
  "size": 0,
  "aggs": {}
}
    ''' % (yestedayTime * 1000, nowTime * 1000)
    r = requests.post(searchTopUrl, data=countInput)
    searchRes = json.loads(r.text)
    totleSearch = searchRes['hits']['total']

    searchInput = '''{
  "query": {
    "filtered": {
      "query": {
        "query_string": {
          "query": "*",
          "analyze_wildcard": true
        }
      },
      "filter": {
        "bool": {
          "must": [
            {
              "range": {
                "timestamp": {
                  "gte": %s,
                  "lte": %s,
                  "format": "epoch_millis"
                }
              }
            }
          ],
          "must_not": []
        }
      }
    }
  },
  "size": 0,
  "aggs": {
    "topN": {
      "terms": {
        "field": "word.raw",
        "size": 10,
        "order": {
          "_count": "desc"
        }
      }
    }
  }
}''' % (yestedayTime * 1000, nowTime * 1000)


    r = requests.post(searchTopUrl, data=searchInput)
    searchRes = json.loads(r.text)
    topSearchList = searchRes['aggregations']['topN']['buckets']

    searchWordQueryTempl = '''
    {
  "size" : 5,
  "query" : {
    "simple_query_string" : {
      "query" : "%s",
      "fields" : [ "author^5.0", "title^10.0", "subtitle^1.0" ]
    }
  },
  "_source" : {
    "includes" : [ "title", "author" ],
    "excludes" : [ ]
  }
}
    '''

    htmlTemp = u'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>读书日报</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/echarts/3.6.2/echarts.min.js"></script>
</head>
<body>


<div id="main">


        <p class="sample name" style="
    text-indent: 0.5rem;
    color: #00BFFF;
">图书汇总：</p>
    <div style=" line-height:2px; width:76px; background-color:#02b884; margin-top:8px;">&nbsp;</div>


    <p>图书总数：%s, 已上线图书总数：%s, 上周更新图书总数： %s</p>
<br>

        <p class="sample name" style="
    text-indent: 0.5rem;
    color: #00BFFF;
">搜索情况：</p>
    <div style=" line-height:2px; width:76px; background-color:#02b884; margin-top:8px;">&nbsp;</div>
    
    <p>搜索总次数：<b>%s</b> &nbsp;&nbsp; <a href="http://123.57.36.133:15601/goto/f9e58e060ea3fae708d9c229bb3ad450">查看详情</a>
    </p>
    
<table border="1">
  <tr>
    <th>检索词：次数</th>
    <th>命中结果（书名 -- 作者）</th>
  </tr>
  <tr>
    ''' % (str(totleCount), str(onlineCount), str(updateCount), str(totleSearch))

    for topHit in topSearchList:
        word = topHit['key']
        wordLeft = u'''
        <th rowspan="5">%s： %s</th>
                        ''' % (word, str(topHit['doc_count']))
        htmlTemp = htmlTemp + wordLeft
        searchWordQuery = searchWordQueryTempl % (word)
        w = requests.post('http://123.56.66.33:19200/dushu/_search', data=searchWordQuery.encode('utf-8'))
        searchWordRes = json.loads(w.text)
        for hit in searchWordRes['hits']['hits']:
            title = hit['_source']['title']
            author = hit['_source']['author']

            wordTemp = u'''
            <td><b>%s</b> -- %s</td>
            </tr>
            <tr>''' % ( title, author)

            htmlTemp = htmlTemp + wordTemp
    htmlTemp = htmlTemp[0:-4] + '''</table>
                                </div>
                                </body>
                                </html>
                                '''
    send(htmlTemp)


def send(msg):
    mail_host= SMTP_EXMAIL_QQ_COM  #设置服务器
    mail_user= NO_REPLY_TATATIMES_COM  #用户名
    mail_pass= MAILPASS  #口令

    sender = NOREPLAYEMAIL
    # receivers = [MANAGER_TATATIMES_COM, "zyq@tatatimes.com"]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    # receivers = ['467959945@qq.com']
    receivers = dushuDailyReportReciever



    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    message = MIMEText(msg, 'html', 'utf-8')
    message['From'] = Header("塔塔时代", 'utf-8')
    message['To'] =  Header('老大们', 'utf-8')

    subject = "读书日报:" + time.strftime('%Y %m-%d  %H:%M', time.localtime(time.time() - 24 * 3600)) \
              + "至" + time.strftime('%Y %m-%d  %H:%M', time.localtime(time.time()))
    message['Subject'] = Header(subject, 'utf-8')


    try:

        smtp = smtplib.SMTP()
        smtp.connect(mail_host)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.set_debuglevel(1)
        smtp.login(mail_user, mail_pass)
        smtp.sendmail(sender, receivers, message.as_string())
        smtp.quit()

        # smtpObj = smtplib.SMTP()
        # smtpObj.connect(mail_host, 465)  # 25 为 SMTP 端口号
        # smtpObj.login(mail_user, mail_pass)
        # smtpObj.sendmail(sender, receivers, message.as_string())
        print "邮件发送成功"
    except smtplib.SMTPException:
        print "Error: 无法发送邮件"



if __name__ == '__main__':
    dushuDailyReport()
    # produceBookSuggest()