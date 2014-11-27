# -*- coding: utf-8 -*-
#
# This file is part of Aggregator.
#
# Copyright (c) 2013 <ahref Foundation -- All rights reserved.
# Author Santosh Singh <santosh@incaendo.com>
#
#This file can not be copied and/or distributed without the express
# permission of <ahref Foundation.
##############################################################################


"""API Key handler class
    class provides function to interact with api_key table

"""

from aggregator import db
from mongokit import *  # NOQA
import time
import uuid


class APIKeyHandler:

    def __init__(self):
        #constructor
        self.collection = db.apikey

    def save(self, application_name):
        """Save method

            Method use to insert new api key
            :key: new api key. Should be unique and a random 16 digit code
            :application_name: application name which will be using this key
        """
        key = uuid.uuid4()
        key_data = {
            'key': key.hex,
            'application': application_name,
            'status': 1,
            'created': int(time.time())
        }
        id = self.collection.insert(key_data)
        return str(id)

    def keyCheck(self, key):
        """keyCheck function for checking if key exists or not

            :key: Api key to check weather it exists or not and its status
                  should be 1(active)
        """
        conditions = {
            'key': key,
            'status': 1
        }
        data = self.collection.find(conditions)
        return_data = []
        for key in data:
            return_data.append(key)
        return return_data

    def loadKey(self, id):
        """loadKey function to laod api key based on mongo id

            :id: mongo id
        """
        data = self.collection.find_one({'_id': ObjectId(id)})
        return data

    def delete(self, id):
        """delete function to delete api key based on id

            :id: mongo id
        """
        self.collection.remove({'_id': ObjectId(id)})
