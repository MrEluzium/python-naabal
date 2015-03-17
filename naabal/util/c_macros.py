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

ROTL = lambda uint32, bits: CAST_TO_UINT32((uint32 << bits) | CAST_TO_CHAR(uint32 >> (32 - bits)))

SPLIT_TO_BYTES = lambda uint32: bytearray((uint32 & (0xFF << s)) >> s \
    for s in range(0, 32, 8))

CAST_TO_CHAR = lambda uint32: uint32 & 0xFF
CAST_TO_UINT32 = lambda value: value & 0xFFFFFFFF

COMBINE_BYTES = lambda bytes: reduce(
    lambda p, n: p | (n[0] << n[1]),
    zip(bytes, xrange(0, 32, 8)), 0)
