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

from flask.ext.script import Manager, Server, prompt_bool
from aggregator import app
from functools import wraps
from flask import jsonify, request, render_template
import error_codes
from command import update_image_url
from api_key import APIKeyHandler
from aggregator.add_api_key import AddAPIKey


manager = Manager(app)

app.debug = True

# Turn on debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger=True,
    use_reloader=True,
    host='0.0.0.0',
    port='5002')
)

# check_auth
#
# This method checks the authenticity of the request by verifying the api_key
# and the response format against the defined api_key and the format


def check_auth(api_key, format):
    flag = False
    errorCode = ''
    apikey = APIKeyHandler()
    valid_key = apikey.keyCheck(api_key)
    if len(valid_key) > 0:
        flag = True
    else:
        errorCode = error_codes.INVALID_API_KEY
    if not format in app.config['ALLOWED_FORMATS']:
        errorCode = error_codes.UNSUPPORTED_RESPONSE_FORMAT
        flag = False
    return {'status': flag, 'message': errorCode}


def authenticate(message=[]):
    if len(message) == 0:
        message = error_codes.GENERIC_ERROR
    data = {'errorCode': message[0], 'errorMessage': message[1]}
    resp = api_response('false', data)
    return resp


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = kwargs['api_key']
        if not api_key:
            return authenticate()

        auth_result = check_auth(api_key, kwargs['format'])
        if auth_result['status'] is False:
            return authenticate(auth_result['message'])
        return f(*args, **kwargs)

    return decorated

# api_response
#
# This method returns the response to the request in json format
# If the requested format is not supported it returns a error message


def api_response(status, data):
    format = request.view_args['format']
    if not format:
        message = {'status': 'false', 'data': {'errorCode': error_codes.UNSUPPORTED_RESPONSE_FORMAT[0], 'errorMessage': error_codes.UNSUPPORTED_RESPONSE_FORMAT[1]}}     # NOQA
        resp = jsonify(message)
        resp.status_code = 200
    elif not format in app.config['ALLOWED_FORMATS']:
        message = {'status': 'false', 'data': {'errorCode': error_codes.UNSUPPORTED_RESPONSE_FORMAT[0], 'errorMessage': error_codes.UNSUPPORTED_RESPONSE_FORMAT[1]}}    # NOQA
        resp = jsonify(message)
        resp.status_code = 200
    elif format == 'json':
        message = {'status': status, 'data': data}
        resp = jsonify(message)
        resp.status_code = 200
    return resp


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def index_page():
    return render_template('index.html')


@manager.option('-o', '--object', dest='objectId', required=True)
@manager.option('-p', '--prevurl', dest='oldUrl', required=True)
@manager.option('-t', '--targeturl', dest='newUrl', required=True)
@manager.option('-m', '--mode', dest='mode', required=False)
def update_url(objectId, oldUrl, newUrl, mode):
    """
    Update url script. Available options:
    -o: all or particular object id
    -p: previous url
    -t: new targeted url
    -m: mode. Optional. Possible value is dryrun
    """
    optionmode = 'run'
    if mode and mode != "dryrun":
        print "Only allowed value for mode is dryrun"
        exit(0)
    else:
        optionmode = mode
    if prompt_bool("Are you sure you want to replace image base url from  %s to %s" % (oldUrl, newUrl)):  # NOQA
        options = {'objectId': objectId, 'oldUrl': oldUrl, 'newUrl': newUrl,
                   'mode': optionmode}
        update_image_url(options)

manager.add_command('add_api_key', AddAPIKey())


def main():
    manager.run()

if __name__ == "__main__":
    main()
