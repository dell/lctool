#!/usr/bin/python
# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:
"""
"""

from __future__ import generators

import sys
import os
import unittest

class TestCase(unittest.TestCase):
    def setUp(self):
        if globals().get('lcctool'): del(lcctool)
        for k in sys.modules.keys():
            if k.startswith("lcctool"):
                del(sys.modules[k])

    def tearDown(self):
        if globals().get('lcctool'): del(lcctool)
        for k in sys.modules.keys():
            if k.startswith("lcctool"):
                del(sys.modules[k])

    def testSAMPLE(self):
        print 'hello world'


if __name__ == "__main__":
    import test.TestLib
    sys.exit(not test.TestLib.runTests( [TestCase] ))
