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

from naabal.formats.big.hw1 import HomeworldBigFile

class TestFormatsBigHomeworld1(unittest.TestCase):
    def setUp(self):
        self.bigfile = HomeworldBigFile('/dev/null')

    def test_filename_coding(self):
        TEST_FILENAME = 'test/path/to/file.ext'

        self.assertEqual(TEST_FILENAME, self.bigfile._decode_filename(
            self.bigfile._encode_filename(TEST_FILENAME)))

    def test_filename_normalization(self):
        TEST_FILENAME = 'test/path/to/file.ext'

        self.assertEqual(TEST_FILENAME, self.bigfile._normalize_filename(
            self.bigfile._denormalize_filename(TEST_FILENAME)))

if __name__ == '__main__':
    unittest.main()
