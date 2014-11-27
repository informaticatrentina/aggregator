# -*- coding: utf-8 -*-
#
# This file is part of Aggregator.
#
# Copyright (c) 2013 <ahref Foundation -- All rights reserved.
# Author Santosh Singh <santosh@incaendo.com>
#
#This file can not be copied and/or distributed without the express permission
#of <ahref Foundation.
##############################################################################


"""
Aggregator
======================
"""
from mongokit import *  # NOQA
from aggregator import db


def update_image_url(option):
    conditions = {}
    cnt = 0
    if option['objectId'] == 'all':
        data = db.entry.find({}, {'_id': 1, 'links': 1})
    else:
        conditions['_id'] = ObjectId(option['objectId'])
        data = db.entry.find(conditions, {'_id': 1, 'links': 1})
    for entry in data:
        if 'links' in entry and len(entry['links']) > 0:
            for link in entry['links']:
                for item in entry['links'][link]:
                    if 'uri' in item:
                        if item['uri'].find(option['oldUrl']) > -1:
                            cnt = replace_image_url(entry, item, option, cnt)
    if option['mode'] == 'dryrun':
        print """ total %s entries will be updated by this script.
           In order to update run script without -m
        """ % (cnt)
    else:
        print "total %s entries are updated" % (cnt)


def replace_image_url(entry, item, option, cnt):
    if option['mode'] == "dryrun":
        cnt = cnt + 1
    else:
        cnt = cnt + 1
        item['uri'] = item['uri'].replace(option['oldUrl'], option['newUrl'])
        #now save links back
        if '_id' in entry:
            id = entry['_id']
            entry.pop('_id')
            db.entry.update({'_id': ObjectId(id)}, {'$set': entry})
    return cnt
