#!/usr/bin/env python2.7
# encoding: utf-8

"""
tests.py

"""
import os
import unittest

from application import create_app
from application.config import Testing, Development

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app(config=Testing)
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        self.config = self.app.application.config

    def tearDown(self):
        pass

    def test_home_redirects(self):
        rv = self.app.get('/')
        assert rv.status_code == 302

if __name__ == '__main__':
    unittest.main()