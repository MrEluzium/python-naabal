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

import zlib
import datetime
import calendar
import os
import logging

try:
    # py2
    from cStringIO import StringIO
except ImportError:
    try:
        # py2 on some platform without cStringIO
        from StringIO import StringIO
    except ImportError:
        # py3k
        from io import StringIO


class classproperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


def split_by(iterable, chunk_size):
    return (iterable[pos:pos+chunk_size] for pos in xrange(0, len(iterable), chunk_size))

def crc32(data):
    return zlib.crc32(data) & 0xFFFFFFFF

def unpack_key(key):
    return bytearray(key.strip().decode('base64'))

def timestamp_to_datetime(ts):
    return datetime.datetime.utcfromtimestamp(float(ts))

def datetime_to_timestamp(dt):
    return int(calendar.timegm(dt.utctimetuple()))

def pad_null_string(s, size):
    return s + ('\x00' * (size - len(s)))

def trim_null_string(s):
    return s.rstrip('\x00')

# NullHandler was added in py2.7
if hasattr(logging, 'NullHandler'):
    NullHandler = logging.NullHandler
else:
    class NullHandler(logging.Handler):
        def handle(self, record):
            pass

        def emit(self, record):
            pass

        def createLock(self):
            self.lock = None

LOG_FORMAT = logging.Formatter('[%(asctime)s] %(levelname)8s - %(name)s: %(message)s')
