#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import random

import requests

from Config import ipProxyServerUrl, minPIPCount


def getAvailableIPs(count=-1,types=0,country=u'国内', area=''):
    if count != -1:
        url = ipProxyServerUrl + "?count=" + str(count) + '&types=' + str(types) + '&country=' + country
    else:
        url = ipProxyServerUrl + '?types=' + str(types) + '&country=' + country

    if area != '':
        url = url + '&area=' + area

    r = requests.get(url)
    ip_ports = json.loads(r.text)

    return ip_ports


def deletByIP(ip):
    url = ipProxyServerUrl + 'delete?ip=' + ip
    r = requests.get(url)
    print 'delete proxy ip, ',ip, ', resp:',r.text


def getProxy(renew = False):
    global pIPs, globalProxyCount,pipObj
    # while 1:
    try:
        # count = 100
        if len(pIPs) < minPIPCount:
            # 代理ip太少，重新获取
            pIPs = getAvailableIPs()
        globalProxyCount = globalProxyCount + 1
        if globalProxyCount % 100 == 0 or renew:
            pipObj = random.choice(pIPs)
            print 'globalProxyCount:',str(globalProxyCount), ' change proxyIp to ',str(pipObj)
            pIPs.remove(pipObj)
            globalProxyCount = 0

        # randomPIpIndex = random.randint(0, len(pIPs) - 1)
        # pipObj = pIPs[randomPIpIndex]
        pIp = pipObj[0]
        pPort = pipObj[1]

        # del pIPs[randomPIpIndex]
        # pIPs.remove(pipObj)

        # 删除ip
        # deletByIP(pIp)
        proxy = {
            'http': 'http://%s:%s' % (pIp, pPort),
            'https': 'http://%s:%s' % (pIp, pPort)
        }
        return proxy
    except Exception as e:
        print 'get proxy exception: ',e