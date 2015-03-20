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

from itertools import izip

from naabal.util import split_by
from naabal.util.c_macros import COMBINE_BYTES, SPLIT_TO_BYTES, ROTL, CAST_TO_CHAR


class GearboxCrypt(object):
    def __init__(self, data_size, local_key, global_key):
        self._data_size = data_size
        self._key_size = len(local_key)
        self._encryption_key = self._combine_keys(local_key, global_key)

    @property
    def encryption_key(self):
        return self._encryption_key

    def decrypt(self, data, offset=0):
        data = bytearray(data)
        return ''.join(chr(CAST_TO_CHAR(c + self._encryption_key[(offset + i) % self._key_size])) \
            for i, c in izip(xrange(len(data)), data))

    def encrypt(self, data, offset=0):
        data = bytearray(data)
        return ''.join(chr(CAST_TO_CHAR(c - self._encryption_key[(offset + i) % self._key_size])) \
            for i, c in izip(xrange(len(data)), data))

    def _combine_keys(self, local_key, global_key):
        local_key = [COMBINE_BYTES(bytes) for bytes in split_by(local_key, 4)]
        global_key = [COMBINE_BYTES(bytes) for bytes in split_by(global_key, 4)]
        combined_key = bytearray(self._key_size)

        for i in xrange(0, self._key_size, 4):
            c = local_key[i / 4]
            for b in range(4):
                bytes = SPLIT_TO_BYTES(ROTL(c + self._data_size, 8))
                for j in range(4):
                    c = global_key[CAST_TO_CHAR(c ^ bytes[j])] ^ (c >> 8)
                combined_key[i + b] = CAST_TO_CHAR(c)
        return combined_key
