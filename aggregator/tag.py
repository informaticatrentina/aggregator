# -*- coding: utf-8 -*-
#
# This file is part of Aggregator.
#
# Copyright (c) 2013 <ahref Foundation -- All rights reserved.
# Author Sankalp Mishra <sankalp@incaendo.com>
#
#This file can not be copied and/or distributed without the express permission of <ahref Foundation. # NOQA
##############################################################################


"""
Aggregator
======================
"""

from flask import Blueprint
from aggregator.models import Tag  # NOQA
from aggregator import db
from mongokit import *  # NOQA

tag = Blueprint('tag', __name__, template_folder='templates')

# TagManager
#
# This class is responsible for handling the saving and retrieving of tags


class TagManager:
    def __init__(self):
        self.collection = db.tag

    def save(self, tags):
        for name in tags:
            conditions = {}
            conditions['slug'] = tags['slug']
        data = db.tag.find_one(conditions)
        newtag = {}
        if data is None:
            newtag['entry_count'] = 1
            if 'name' in tags:
                newtag['name'] = tags['name']
            if 'slug' in tags:
                newtag['slug'] = tags['slug']
            if 'weight' in tags:
                newtag['weight'] = tags['weight']
            id = db.tag.insert(newtag)
        else:
            entry_count = data['entry_count'] + 1
            db.tag.update({'_id': data['_id']}, {'$set': {'entry_count': entry_count}})    # NOQA
            id = data['_id']
        return id

    def remove(self, tags):
        tag = db.tag.find({'slug': tags})
        for tags in tag:
            entry_count = tags['entry_count'] - 1
            if entry_count == 0:
                db.tag.remove({'_id': tags['_id']})
            else:
                db.tag.update({'_id': ObjectId(tags['_id'])}, {'$set': {'entry_count': entry_count}})   # NOQA
