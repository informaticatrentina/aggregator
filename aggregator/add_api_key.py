# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 <ahref Foundation -- All rights reserved.
# Author: Santosh Singh <santosh@incanedo.com>
#
# This file is part of the Aggregator Project
#
# This file can not be copied and/or distributed without the express
# permission of <ahref Foundation.
#
###############################################################################

'''
Convenience Module for adding new Api key
'''

from flask.ext.script import Command, Option
from aggregator import db
import time


class AddAPIKey(Command):
    """Add new API Key"""

    option_list = (
        Option('--key', '-k', dest='key',
               help='New api key to be added', required=True),
        Option('--application', '-a', dest='application_name',
               help='New application name', required=True),
    )

    def run(self, key, application_name):
        """add new key"""
        data = {'key': key, 'application': application_name, 'status': 1,
                'created': int(time.time())}
        id = db.apikey.insert(data)
        if id is not None:
            print 'Api key added'
