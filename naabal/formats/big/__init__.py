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


import struct

from naabal.errors import BigFormatException
from naabal.util import classproperty


class BigFile(object):
    _handle = None
    _mode = None
    _name = None
    _closed = True
    softspace = 0

    @property
    def closed(self):
        return self._closed

    @property
    def encoding(self):
        return None

    @property
    def mode(self):
        return self._mode

    @property
    def name(self):
        return self._name

    @property
    def newlines(self):
        return None

    def __init__(self, filename, mode='r'):
        handle = open(filename, mode)
        self._mode = mode
        self._closed = False
        self._name = handle.name
        self._handle = handle

    def __iter__(self):
        return self

    def close(self):
        handle = self._handle
        self._handle = None
        self._name = None
        self._mode = None
        self._closed = True
        return handle.close()

    def flush(self):
        self._handle.flush()

    def fileno(self):
        if self.closed:
            return None
        else:
            return self._handle.fileno()

    def isatty(self):
        if self.closed:
            return False
        else:
            return self._handle.isatty()

    def next(self):
        raise StopIteration()

    def read(self, size): pass
    def readline(self, size): pass
    def readlines(self, sizehint): pass
    def xreadlines(self): pass

    def seek(self, offset, whence): pass
    def tell(self): pass

    def truncate(self, size=None):
        pass

    def write(self, data): pass
    def writelines(self, seq): pass

class BigSection(object):
    STRUCTURE           = []
    _data               = None

    def __init__(self, data=None):
        self._data = {key: None for key in self.keys}
        if data is not None:
            self.populate(data)

    def __getitem__(self, key):
        return self._data.get(key)

    def __setitem__(self, key, value):
        return self._data.set(key, value)

    def __iter__(self):
        return iter(self.keys)

    def __repr__(self):
        return repr(self._data)

    def __str__(self):
        return str(self._data)

    @classproperty
    @classmethod
    def data_size(cls):
        return struct.calcsize(cls.data_format)
    __len__ = data_size

    @classproperty
    @classmethod
    def data_format(cls):
        return '<' + ''.join(e['fmt'] * e['len'] for e in cls.STRUCTURE)

    @classproperty
    @classmethod
    def keys(cls):
        return [e['key'] for e in cls.STRUCTURE]

    def unpack(self, data):
        if len(data) != self.data_size:
            raise BigFormatException('Data length is not expected')
        else:
            return struct.unpack(self.data_format, data)

    def populate(self, data):
        unpacked_data = self.unpack(data)
        idx = 0
        for struct_member in self.STRUCTURE:
            if struct_member['len'] == 1:
                self._data[struct_member['key']] = struct_member['read'](unpacked_data[idx])
            else:
                self._data[struct_member['key']] = \
                    struct_member['read'](unpacked_data[idx:idx+struct_member['len']])
            idx += struct_member['len']

        self.check()

    def check(self):
        return True
