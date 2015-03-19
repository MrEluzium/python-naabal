#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2015 Alex Headley <aheadley@waysaboutstuff.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest

from naabal.util.c_macros import *

class TestUtilCMacros(unittest.TestCase):
    def test_cast_to_char(self):
        test_value1 = 0xFFFFFFFF
        test_value2 = 0x11223344

        self.assertEqual(0xFF, CAST_TO_CHAR(test_value1))
        self.assertEqual(0x44, CAST_TO_CHAR(test_value2))

    def test_split_to_bytes(self):
        test_value1 = 0x11223344

        self.assertEqual(bytearray([0x44, 0x33, 0x22, 0x11]), SPLIT_TO_BYTES(test_value1))

    def test_cast_to_uint32(self):
        test_value1 = 0x11223344
        test_value2 = 0xFF
        test_value3 = 0xFFFFFFFFFF

        self.assertEqual(test_value1, CAST_TO_UINT32(test_value1))
        self.assertEqual(test_value2, CAST_TO_UINT32(test_value2))
        self.assertEqual(0xFFFFFFFF, CAST_TO_UINT32(test_value3))

    def test_combine_bytes(self):
        test_value1 = 0x11223344

        self.assertEqual(test_value1, COMBINE_BYTES(bytearray([0x44, 0x33, 0x22, 0x11])))

    def test_rotl(self):
        test_value1 = 0xFFFFFFFFFF
        test_value2 = 0x1122334455
        test_value3 = 0x44332211
        test_value4 = 0x14827E85E

        self.assertEqual(0xFFFFFFFF, ROTL(test_value1, 8))
        self.assertEqual(0x33445522, ROTL(test_value2, 8))
        self.assertEqual(0x33221144, ROTL(test_value3, 8))
        self.assertEqual(0x27E85E48, ROTL(test_value4, 8))

if __name__ == '__main__':
    unittest.main()
