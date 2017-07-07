#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
处理其他源中默认图片，更换成我们的默认图片
@author: zyq
'''
from Config import DefaultImg


def loadDefaultImgs():
    fdimgs = open('local/defaultImgs.txt')
    defaultImgSet = set()
    while 1:
        imgUrl = fdimgs.readline()
        if not imgUrl:
            break
        imgUrl = imgUrl.replace('\n', '')
        defaultImgSet.add(imgUrl)

    return defaultImgSet

defaultImgSet = loadDefaultImgs()

def checkDefaultImg(img):
    '''
    img为空或判断出是其他源的默认图片，返回我默认图片，否则返回img
    :param img: 
    :return: 
    '''
    if not img or '' == img:
        return DefaultImg
    if img in defaultImgSet:
        return DefaultImg
    return img