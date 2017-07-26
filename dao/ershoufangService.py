#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''

@author: zyq
'''
import time

# from selenium.webdriver.phantomjs import webdriver
from selenium import webdriver

from Config import PHANTOMJS_BIN_PATH, FANG_HOST, ossBaseUrl, ossOpenBaseUrl
from dao.aliyunOss import upload2Bucket
from dao.connFactory import getDushuConnCsor
from util.timeHelper import getToday

emailTempl = u'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>住建委数据</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/echarts/3.6.2/echarts.min.js"></script>
</head>
<body>

<div id="main" style="width: 1200px;height:600px;"></div>
<script type="text/javascript">
    var myChart = echarts.init(document.getElementById('main'));

    option = {
        title: {
            text: '住建委数据'
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['存量网签', '存量住宅网签', '新发布', '新发布住宅', '可售房源', '可售住宅']
        },
        toolbox: {
            show: true,
            feature: {
                dataZoom: {
                    yAxisIndex: 'none'
                },
                dataView: {readOnly: false},
                magicType: {type: ['line', 'bar']},
                restore: {}
            }
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: %s
        },
        yAxis: [{
            type: 'value',
            max: 1800,
            axisLabel: {
                formatter: '{value} 套'
            }
        }, {
            type: 'value',
            min: 10000,
            axisLabel: {
                formatter: '{value} 套'
            }
        }],
        series: [
            {
                name: '存量网签',
                type: 'line',
                data: %s,
                markPoint: {
                    data: [
                        {type: 'max', name: '最大值'}
                    ]
                }
            },
            {
                name: '存量住宅网签',
                type: 'line',
                data: %s,
                markPoint: {
                    data: [
                        {type: 'max', name: '最大值'}
                    ]
                }
            },
            {
                name: '新发布',
                type: 'line',
                data: %s,
                markPoint: {
                    data: [
                        {type: 'max', name: '最大值'}
                    ]
                }
            },
            {
                name: '新发布住宅',
                type: 'line',
                data: %s,
                markPoint: {
                    data: [
                        {type: 'max', name: '最大值'}
                    ]
                }
            },
            {
                name: '可售房源',
                type: 'line',
                xAxisIndex: 0,
                yAxisIndex: 1,
                data: %s,
                markPoint: {
                    data: [
                        {type: 'max', name: '最大值'}
                    ]
                }
            },
            {
                name: '可售住宅',
                type: 'line',
                xAxisIndex: 0,
                yAxisIndex: 1,
                data: %s,
                markPoint: {
                    data: [
                        {type: 'max', name: '最大值'}
                    ]
                }
            }
        ]
    };

    myChart.setOption(option);
</script>
</body>
</html>
'''

def getAll():
    conn, csor = getDushuConnCsor()

    csor.execute("select DATE_FORMAT(updateTime, '%Y-%m-%d') as day, keshou_count, keshou_area, keshou_zhuzai_count"
                 ", keshou_zhuzai_area, new_publish_count, new_publish_area, new_publish_zhuzai_count"
                 ", new_publish_zhuzai_area, sign_count, sign_area, sign_zhuzai_count, sign_zhuzai_area from cn_test "
                 "order by id desc limit 100")
    conn.commit()
    res = csor.fetchall()

    return res

def getChartAsStr():
    res = getAll()

    days = list()
    keshou_counts = list()
    keshou_zhuzai_counts = list()
    new_publish_counts = list()
    new_publish_zhuzai_counts = list()
    sign_counts = list()
    sign_zhuzai_counts = list()

    for rec in res[::-1]:
        days.append(str(rec[0]))
        keshou_counts.append(int(rec[1]))
        keshou_zhuzai_counts.append(int(rec[3]))
        new_publish_counts.append(int(rec[5]))
        new_publish_zhuzai_counts.append(int(rec[7]))
        sign_counts.append(int(rec[9]))
        sign_zhuzai_counts.append(int(rec[11]))

    chartsStr = emailTempl % (days,
        sign_counts,
        sign_zhuzai_counts,
        new_publish_counts,
        new_publish_zhuzai_counts,
        keshou_counts,
        keshou_zhuzai_counts)

    return chartsStr

def getImgTag():
    return  u'<br><p><b>历史数据(图片可能被邮箱隐藏)：<b></p><img src="' + shanpshot() + u'"/><br><a href="http://' + FANG_HOST + u'/fang"><p>详情</p></a>'

def shanpshot():
    driver = webdriver.PhantomJS(
        executable_path=(r"%s" % PHANTOMJS_BIN_PATH))
    driver.get('http://0.0.0.0:10008/fang')

    time.sleep(60)

    img = driver.find_element_by_css_selector('#main').screenshot_as_png

    upload2Bucket(getToday() + '.png', img)
    driver.quit()
    return  ossOpenBaseUrl  + getToday() + '.png'