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
import time
import os

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

class FileInFile(object):
    def __init__(self, parent_handle, offset, size, writeable=True):
        self._handle        = parent_handle
        self._writeable     = writeable and ('w' in self._handle.mode)
        self._offset        = offset
        self._size          = size
        self._position      = 0

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()

    def __repr__(self):
        return '<{4} ("{0}":{1:d}+{2:d}@{3:d})>'.format(
            self._handle.name, self._offset, self._size, self._position,
            self.__class__.__name__)

    def tell(self):
        return self._position

    def seek(self, pos, mode=os.SEEK_SET):
        if mode == os.SEEK_SET:
            self._position = pos
        elif mode == os.SEEK_CUR:
            self._position += pos
        elif mode == os.SEEK_END:
            self._position = size + pos
        self._position = self._constrain_position(self._position)

    def read(self, size=None):
        size = self._normalize_size(size)
        self._handle.seek(self._offset + self._position)
        self._position += size
        return self._handle.read(size)

    def write(self, data):
        if self._writeable:
            if len(data) > self._normalize_size(len(data)):
                raise IOError('Attempted to write bytes beyond end of FileInFile')
            else:
                self._handle.seek(self._offset + self._position)
                self._position += len(data)
                self._handle.write(data)
        else:
            raise IOError('FileInFile is not writeable')

    def flush(self):
        return self._handle.flush()

    def close(self): pass
    def truncate(self, size=0): pass

    def fileno(self):
        return self._handle.fileno()

    def _normalize_size(self, size):
        if size is None:
            size = self._size - self._position
        return min(size, self._size - self._position)

    def _constrain_position(self, pos):
        pos = min(pos, self._size)
        pos = max(pos, 0)
        return pos


def split_by(iterable, chunk_size):
    return (iterable[pos:pos+chunk_size] for pos in xrange(0, len(iterable), chunk_size))

def crc32(data):
    return zlib.crc32(data) & 0xFFFFFFFF

def unpack_key(key):
    return bytearray(key.strip().decode('base64'))

def timestamp_to_datetime(ts):
    return datetime.datetime.utcfromtimestamp(float(ts))

def datetime_to_timestamp(dt):
    return int(time.mktime(dt.utctimetuple()))
