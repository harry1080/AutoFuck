#!/usr/bin/env python
# -*- coding: utf-8 -*- # 
__author__ = 'fengxuan'

import requests
import hashlib,sys
import gevent
from gevent.queue import Queue
from gevent import monkey
import time

from .log import logger
from .parser import checkcms

monkey.patch_all()

class gwhatweb(object):
    def __init__(self, url, webdata):
        self.tasks = Queue()
        self.url = url.rstrip("/")
        self.cmsdict = {}
        self.cmsname = None
        for i in webdata:
            self.tasks.put(i)

        print("webdata total:%d"%len(webdata))

    def _GetMd5(self, body):
        m2 = hashlib.md5()
        m2.update(body)
        return m2.hexdigest()

    def _clearQueue(self):
        while not self.tasks.empty():
            self.tasks.get()

    def _worker(self):
        data = self.tasks.get()
        test_url = "{0}{1}".format(self.url, data["url"])
        req = None
        try:
            print("[!]spider website {0}".format(test_url))
            req = requests.get(test_url, timeout=10)
            #
            # rtext = req.text
            # if rtext is None:
            #     return
        except:
            rtext = ''

        if not req:
            return False

        result = checkcms(req, data)

        if result:

            if result > 100:
                logger.info('web is  {0} finger: {1}'.format(data['name'], data['url']))
                return data['name']

            if data['name'] not in self.cmsdict:
                logger.info('web look like {0}'.format(data['name']))
                self.cmsdict[data['name']] = data['weight']
                logger.info('cms weight:{}'.format(self.cmsdict[data['name']]))
            else:
                self.cmsdict[data['name']] += data['weight']
                logger.info('cms weight:{}'.format(self.cmsdict[data['name']]))
                if self.cmsdict[data['name']] > 100:
                    logger.info('web is  {0} finger: {1}'.format(data['name'], data['url']))

                    return data['name']
        return False


    def _boss(self):
        while not self.tasks.empty():
            flag = self._worker()
            if flag:
                self.cmsname = flag
                self._clearQueue()


    def whatweb(self, maxsize=5):
        allr = [gevent.spawn(self._boss) for i in range(maxsize)]
        gevent.joinall(allr)
        return self.cmsname

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usag:python gwhatweb.py http://www.xxx.com")
    else:
        url = sys.argv[1]
        g = gwhatweb(url)
        g.whatweb(1000)