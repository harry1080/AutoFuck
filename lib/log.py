#!/usr/bin/env python
# -*- coding: utf-8 -*- # 
__author__ = 'fengxuan'

import logging

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(message)s',
                    datefmt='%Y:%m:%d %H:%M:%S')
logger = logging.getLogger('running')