# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 <ahref Foundation -- All rights reserved.
# Author: Daniele Pizzolli <daniele@ahref.eu>
#
# This file is part of the aggregator project.
#
# This file can not be copied and/or distributed without the express
# permission of <ahref Foundation.
#
###############################################################################

"""
Local Settings Template
=======================

This file is not loaded by the application by default.

This file contains all the relevant settings for local configuration,
especially the sensible ones (e.g. passwords), to be copied and changed by the
configuration manager and loaded using the ``AGGREGATOR_SETTINGS`` environment
variable.
"""

# MongoDB
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_DATABASE = 'DATABASE'
MONGODB_USERNAME = 'USERNAME'
MONGODB_PASSWORD = 'PASSWORD'

# API Key
API_KEY = 'KEY'

# URL (http://www.example.com/)
BASE_URL = 'URL'

# Logs
LOG_FILE = 'PATH'
