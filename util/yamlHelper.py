#!/usr/bin/python
# -*- coding: UTF-8 -*-
import yaml


def loadYaml(fileName):
    try:
        conf =yaml.load(file(fileName))
    except Exception as e:
        print e
        return None
    return conf


def dumpDict2Yaml(fileName,dct):
    f = open(fileName, 'wb')
    yaml.dump(dct, f)
    f.close()