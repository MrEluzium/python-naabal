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
from cStringIO import StringIO

from naabal.util.bitio import BitReader, BitWriter

TEST_DATA1_BYTE = 0xDE
TEST_DATA1_CHAR = '\xDE'

class TestUtilBitIO(unittest.TestCase):
    def setUp(self):
        self.output_buffer = StringIO()
        self.reader = BitReader(StringIO(TEST_DATA1_CHAR))
        self.writer = BitWriter(self.output_buffer)

    def test_write_bit(self):
        # 0xD0
        self.writer.write_bit(0x01)
        self.writer.write_bit(0x01)
        self.writer.write_bit(0x00)
        self.writer.write_bit(0x01)
        # 0x0E
        self.writer.write_bit(0x01)
        self.writer.write_bit(0x01)
        self.writer.write_bit(0x01)
        self.writer.write_bit(0x00)

        self.writer.flush()
        self.assertEqual(TEST_DATA1_CHAR, self.output_buffer.getvalue())

    def test_write_bits(self):
        self.writer.write_bits(TEST_DATA1_BYTE, 8)
        self.writer.flush()
        self.assertEqual(TEST_DATA1_CHAR, self.output_buffer.getvalue())

    def test_read_bit(self):
        # 0xD0
        self.assertEqual(0x01, self.reader.read_bit())
        self.assertEqual(0x01, self.reader.read_bit())
        self.assertEqual(0x00, self.reader.read_bit())
        self.assertEqual(0x01, self.reader.read_bit())
        # 0x0E
        self.assertEqual(0x01, self.reader.read_bit())
        self.assertEqual(0x01, self.reader.read_bit())
        self.assertEqual(0x01, self.reader.read_bit())
        self.assertEqual(0x00, self.reader.read_bit())

    def test_read_bits(self):
        self.assertEqual(TEST_DATA1_BYTE, self.reader.read_bits(8))

if __name__ == '__main__':
    unittest.main()
