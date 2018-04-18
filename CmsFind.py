#!/usr/bin/env python
# -*- coding: utf-8 -*- #
__author__ = 'fengxuan'

import time
import json
import sys
import os
from multiprocessing import Process

from lib.gwhatweb import gwhatweb

absolutepath = sys.path[0]



def LoadCmsFingerprint():
    cmsfinger = []
    cmsjson = "{0}{1}json/testcms.json".format(absolutepath, os.sep)
    with open(cmsjson) as f:
        cmsfinger = json.load(f)

    return cmsfinger

def LoadTargetFile():
    data = []
    with open('target.txt') as f:
        for line in f.readlines():
            data.append(line.strip())

    return data

def cmsfind(url, cmsfinger):
    p = gwhatweb(url, cmsfinger)
    res = p.whatweb()
    result = "{0} is {1}".format(url, res)
    print(result)


def main():
    start = time.time()
    target = LoadTargetFile()
    cmsfinger = LoadCmsFingerprint()

    process_list = []
    for url in target:
        p = Process(target=cmsfind, args=(url,cmsfinger,))
        process_list.append(p)

    for p in process_list:
        p.start()

    for pro in process_list:
        pro.join()

    print("spend {} ".format(time.time() - start))

if __name__ == '__main__':
    main()

