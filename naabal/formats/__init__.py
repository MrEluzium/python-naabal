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
import os

from naabal.util import classproperty, split_by
from naabal.errors import StructuredFileFormatException

class StructuredFile(object):
    STRUCTURE = []

    _handle = None
    _mode = None
    _name = None
    _closed = True
    _data = {}
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
        self.populate()

    def __iter__(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()

    def __repr__(self):
        return repr(self._data)

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

    def read(self, size=None):
        return self._handle.read(size)

    def seek(self, offset, whence=os.SEEK_SET):
        return self._handle.seek(offset, whence)

    def tell(self):
        return self._handle.tell()

    def truncate(self, size=None): pass

    def write(self, data): pass
    def writelines(self, seq): pass

    def populate(self):
        self.seek(0)
        for idx, (key, member_type) in zip(xrange(len(self.STRUCTURE)), self.STRUCTURE):
            if issubclass(member_type, StructuredFileSequence):
                self._data[key] = member_type(self.read(
                    self._get_sequence_length(key) * member_type.CHILD_TYPE.data_size))
            else:
                self._data[key] = member_type(self.read(member_type.data_size))
        self.check()

    def check(self):
        return True

    def _get_sequence_length(self, key):
        raise NotImplemented()

class StructuredFileSection(object):
    ENDIANNESS          = '<'
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

    def __len__(self):
        return self.data_size

    @classproperty
    @classmethod
    def data_size(cls):
        return struct.calcsize(cls.data_format)
    __len__ = data_size

    @classproperty
    @classmethod
    def data_format(cls):
        return cls.ENDIANNESS + \
            ''.join(member['fmt'] * member['len'] for member in cls.STRUCTURE)

    @classproperty
    @classmethod
    def keys(cls):
        return [member['key'] for member in cls.STRUCTURE]

    def unpack(self, data):
        if len(data) != self.data_size:
            raise StructuredFileFormatException('Data length is not expected: %d != %d' % \
                (len(data), self.data_size))
        else:
            return struct.unpack(self.data_format, data)

    def populate(self, data):
        unpacked_data = self.unpack(data)
        idx = 0
        for member in self.STRUCTURE:
            if member['len'] == 1:
                self._data[member['key']] = member['read'](unpacked_data[idx])
            else:
                self._data[member['key']] = \
                    member['read'](unpacked_data[idx:idx+member['len']])
            idx += member['len']

        self.check()

    def check(self):
        return True

class StructuredFileSequence(object):
    CHILD_TYPE      = None
    _data_list      = None

    def __init__(self, data=None):
        if data is not None:
            self.populate(data)

    def __getitem__(self, key):
        return self._data_list[key]

    def __setitem__(self, key, value):
        if not issubclass(value.__class__, self.CHILD_TYPE):
            raise ValueError()
        return self._data_list.set(key, value)

    def __iter__(self):
        return (member for member in self._data_list)

    def __len__(self):
        return len(self._data_list)

    def populate(self, data):
        if len(data) % self.CHILD_TYPE.data_size != 0:
            raise ValueError()
        self._data_list = [self.CHILD_TYPE(chunk) for chunk in split_by(data, self.CHILD_TYPE.data_size)]

    def check(self):
        return all(child.check() for child in self._data_list)
