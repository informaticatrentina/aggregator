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


'''
Database Models test for aggregator
'''

# unittest2 offers TestCase.assertMultiLineEqual that provide a nice
# diff output, sometimes it is called automagically by the old
# assertEqual

try:
    import unittest2 as unittest
except ImportError:
    # NOQA
    import unittest


from nose.plugins.skip import SkipTest


from .. import models


class ExampleTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def first_test(self):
        '''Human readable test name'''
        raise SkipTest('Please start writing real test!')
        silly_example = models
        del(silly_example)
