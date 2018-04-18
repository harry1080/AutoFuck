#!/usr/bin/env python
# -*- coding: utf-8 -*- # 
__author__ = 'fengxuan'

import hashlib
import re
from .log import logger



def _GetMd5(body):
    m2 = hashlib.md5()
    m2.update(body)
    return m2.hexdigest()


def checkcms(req_obj, rule):
    '''
    {"ruletype": "code", "rule": 200, "weight":75}
    :return:
    '''
    # if self.rule['d']
    method = rule['method']
    weight = 0

    if method == 're':
        regu_cont=re.compile(rule['value'], re.I)
        res=regu_cont.match(req_obj.text)
        if res:
            weight = rule['weight']
    elif method == 'md5':
        md5 = _GetMd5(req_obj.text)
        if md5 == rule['value']:
            weight = rule['weight']
    elif method == 'code':
        code = req_obj.status_code
        if code == rule['value']:
            weight = rule['weight']

    return weight
