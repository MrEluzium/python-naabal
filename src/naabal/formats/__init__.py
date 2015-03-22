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
    _data = None
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
        self._load_defaults()

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

    def write(self, data):
        return self._handle.write(data)

    def load(self):
        self.seek(0)
        # this could be done with dict comprehension, except sequences refer back
        # to data that should already be loaded and with a comprehension it isn't
        # assigned to _data until after load() finishes
        self._data = {}
        for key, member_type in self.STRUCTURE:
            self._data[key] = member_type(self)
        self.check()

    def save(self):
        raise NotImplemented()
        self.seek(0)
        for key, member_type in self.STRUCTURE:
            self._data[key].save(self)

    def check(self):
        return True

    def _load_defaults(self):
        self._data = {key: member_type() for key, member_type in self.STRUCTURE}

class StructuredFileSection(object):
    ENDIANNESS          = '<'
    STRUCTURE           = []
    _data               = None

    def __init__(self, handle=None):
        if handle is not None:
            self.load(handle)
        else:
            self._load_defaults()

    def __getitem__(self, key):
        return self._data.get(key)

    def __setitem__(self, key, value):
        return self._data.set(key, value)

    def __iter__(self):
        return iter(self.keys)

    def __repr__(self):
        return repr(self._data)

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

    def load(self, handle):
        self._data = {}
        unpacked_data = self.unpack(handle.read(self.data_size))
        idx = 0
        for member in self.STRUCTURE:
            if member['len'] == 1:
                self._data[member['key']] = member['read'](unpacked_data[idx])
            else:
                self._data[member['key']] = \
                    member['read'](unpacked_data[idx:idx+member['len']])
            idx += member['len']
        self.check()

    def save(self, handle):
        self.check()
        packed_data = struct.pack(self.data_format,
            *(m['write'](self._data[m['key']]) for m in self.STRUCTURE))
        handle.write(packed_data)

    def check(self):
        return True

    def _load_defaults(self):
        self._data = {member['key']: member['default'] for member in self.STRUCTURE}

class StructuredFileSequence(object):
    CHILD_TYPE      = None
    _data_list      = None

    def __init__(self, handle=None):
        if handle is not None:
            self.load(handle)
        else:
            self._load_defaults()

    def __getitem__(self, key):
        return self._data_list[key]

    def __setitem__(self, key, value):
        if not issubclass(value.__class__, self.CHILD_TYPE):
            raise ValueError()
        return self._data_list.set(key, value)

    def __iter__(self):
        return (member for member in self._data_list)

    def __repr__(self):
        return repr(self._data_list)

    def __len__(self):
        return len(self._data_list)

    def load(self, handle):
        self._data_list = [self.CHILD_TYPE(handle) \
            for i in xrange(self._get_expected_length(handle))]

    def save(self, handle):
        for child in self._data_list:
            child.save(handle)

    def check(self):
        return all(child.check() for child in self._data_list)

    def _load_defaults(self):
        self._data_list = []

    def _get_expected_length(self, handle):
        raise NotImplemented()
