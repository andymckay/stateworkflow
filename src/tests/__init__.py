# Copyright: Clearwind Consulting, Ltd.
# License: GPL                                  
# For more info see: http://www.clearwind.ca
#
# $Id$

import unittest
import basic
import advanced

__tests__ = [basic, advanced]
__tests__ = [advanced,]

def suite():
    suite = unittest.TestSuite()
    tests = []
    for test in __tests__:
        tl = unittest.TestLoader().loadTestsFromModule(test)
        tests += tl._tests
    suite._tests = tests
    return suite
