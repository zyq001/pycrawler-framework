#!/usr/bin/python
# -*- coding: UTF-8 -*-
from util.emailHelper import send_email
from util.htmlHelper import getSoupByStr
from util.networkHelper import getContent
from util.timeHelper import getToday

try:
    htmlContent = getContent('')
    soup = getSoupByStr(htmlContent)
    section = soup.select('.portlet')[1]
    terms = section.select("table[bgcolor='#ffffff']")

    assert len(terms) == 4

    keshou = terms[0]
    keshou_count = keshou.select('')
    keshou_area = keshou.select('')
    keshou_zhuzai_count = keshou.select('')
    keshou__zhuzai_area = keshou.select('')


    new_publish = terms[1]
    new_publish_count = keshou.select('')
    new_publish_area = keshou.select('')
    new_publish_zhuzai_count = keshou.select('')
    new_publish_zhuzai_area = keshou.select('')


    sign = terms[3]
    sign_count = keshou.select('')
    sign_area = keshou.select('')
    sign_zhuzai_count = keshou.select('')
    sign_zhuzai_area = keshou.select('')




except Exception as e:
    print 'error:', e
    send_email(msg= unicode(e),subject = u'房产交易抓取异常' + str(getToday()), recievers='467959945@qq.com',)

except AssertionError as e:
    print 'error:', e
    send_email(msg= unicode(e),subject = u'房产交易抓取异常' + str(getToday()), recievers='467959945@qq.com',)
