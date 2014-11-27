#
# Copyright (c) 2013 <ahref Foundation -- All rights reserved.
# Author: Santosh Singh <santosh@incaendo.com>
#
# This file is part of the aggregator project.
#
# This file can not be copied and/or distributed without the express
# permission of <ahref Foundation.
#
###############################################################################


"""
Aggregator
==========
"""

from flask import Flask
from flask.ext.mongokit import Connection

app = Flask(__name__)
app.config.from_object('aggregator.settings')
# Override configuration from the file declared by AGGREGATOR_SETTINGS
app.config.from_envvar('AGGREGATOR_SETTINGS', silent=True)


def conf_logging(app):
    '''Seutp proper loggin'''
    if app.debug is not True:
        import logging
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(app.config['LOG_FILE'],
                                           maxBytes=1024 * 1024 * 100,
                                           backupCount=31)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(name)s - "
                                      "%(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.DEBUG)


conf_logging(app)

# connect to the database
connection = Connection(app.config['MONGODB_HOST'],
                        app.config['MONGODB_PORT'])

db = connection[app.config['MONGODB_DATABASE']]

if app.config['MONGODB_USERNAME'] and app.config['MONGODB_PASSWORD']:
    db.authenticate(
        app.config['MONGODB_USERNAME'],
        app.config['MONGODB_PASSWORD'])


def register_blueprints(app):
    # Prevents circular imports
    from aggregator.entry import entry
    from aggregator.tag import tag
    app.register_blueprint(entry)
    app.register_blueprint(tag)

register_blueprints(app)

if __name__ == '__main__':
    app.run()
