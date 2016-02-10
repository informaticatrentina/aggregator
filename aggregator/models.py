# -*- coding: utf-8 -*-
#
# This file is part of Aggregator.
#
# Copyright (c) 2013 <ahref Foundation -- All rights reserved.
# Author Santosh Singh <santosh@incaendo.com>
#
#This file can not be copied and/or distributed without the express permission
# of <ahref Foundation.
#
##############################################################################

"""
Aggregator
======================
"""

from datetime import datetime

from flask.ext.mongokit import Document

from aggregator import connection

# Entry
#
# This class is used to define structure of a entry in entry collection


class Entry(Document):
    __collection__ = 'entry'
    structure = {
        'status': basestring,
        'guid': basestring,
        'links': [],
        'related': {},
        'creation_date': datetime,
        'modification_date': datetime,
        'publication_date': datetime,
        'title': basestring,
        'author': {'slug': unicode, 'name': basestring},
        'content': [],
        'tags': list,
        'location': {},
        'source': basestring,
        'metadata': {'id': basestring, 'name': basestring, 'description': basestring}  #NOQA
    }
    required_fields = ['content']
    skip_validation = True
    default_values = {'related': {'type': '21212'}, 'location': {'loc':
                                                                 '1234'}}
    use_dot_notation = True

connection.register([Entry])


# Tag
#
# This class is used to define structure of a tag in tag collection


class Tag(Document):
    __collection__ = 'tag'
    structure = {
        'name': basestring,
        'slug': basestring,
        'entry_id': list,
        'entry_count': int,
        'related': {}
    }

connection.register([Tag])

"""Model for api key
    Defines the structure of api key table
"""


class APIKey(Document):
    __collection__ = 'apikey'
    structure = {
        'key': basestring,
        'application': basestring,
        'status': int,
        'created': datetime
    }

connection.register([APIKey])
