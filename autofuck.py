#!/usr/bin/env python
# -*- coding: utf-8 -*- # 
__author__ = 'fengxuan'

import os
import sys
import json
import importlib
import threading
from multiprocessing import Process
from termcolor import cprint

from lib.gwhatweb import gwhatweb
from lib.log import logger


absolutepath = sys.path[0]

def LoadCmsFingerprint():
    cmsfinger = []
    cmsjson = "{0}{1}json/testcms.json".format(absolutepath, os.sep)
    with open(cmsjson) as f:
        cmsfinger = json.load(f)

    return cmsfinger

def LoadPocPlugin():
    cmspocs = []
    cmsjson = "{0}{1}json/data.json".format(absolutepath, os.sep)
    logger.info("Load Poc Plugin ! ------------------")
    with open(cmsjson) as f:
        cmspocs = json.load(f)
    logger.info("Load Poc Plugin Done! ------------------")
    return cmspocs

pocplugin = LoadPocPlugin()

class AutoFuck():
    def __init__(self, url, cms):
        self.url = url
        self.cms = cms

    def attack(self):
        pass

    def verify(self):
        if self.cms not in pocplugin['cms']:
            logger.error("we don't have this cms poc")
            return False

        process_list = []
        for poc in pocplugin['cms'][self.cms]:
            import_module = 'pocs.cms.{cms}.{filename}'.format(cms=self.cms, filename=poc['method'].replace('_BaseVerify', ''))
            p = threading.Thread(target=self.run, args=(import_module,poc,))
            process_list.append(p)

        for p in process_list:
            p.setDaemon(True)
            p.start()

        for pro in process_list:
            pro.join()

    def run(self, import_module, poc):
        method = importlib.import_module(import_module)
        command_run = "method.{classname}('{url}').run()".format(classname=poc['method'], url=self.url)
        eval(command_run)


def loadtargetfile(filename):
    targetlist = []
    with open(filename) as f:
        for line in f.readlines():
            targetlist.append(line.strip())

    return targetlist



def onedragon(url):
    p = gwhatweb(url, cmsfinger)
    cms = p.whatweb()
    if cms:
        at = AutoFuck(url, cms)
        at.verify()
    else:
        cprint("Can't' Recognition this url {0}".format(url))

def main():

    targetlist = loadtargetfile('target.txt')
    process_list = []

    for url in targetlist:
        p = Process(target=onedragon, args=(url,))
        process_list.append(p)

    for p in process_list:
        p.start()

    for pro in process_list:
        pro.join()

if __name__ == '__main__':
    cmsfinger = LoadCmsFingerprint()
    main()