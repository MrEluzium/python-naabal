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
import os.path
from tarfile import _FileInFile

from naabal.formats import StructuredFile, StructuredFileSection, StructuredFileSequence
from naabal.util import StringIO
from naabal.util.gbx_crypt import GearboxCrypt
from naabal.errors import GearboxEncryptionException


class BigInfo(object):
    _bigfile        = None
    _offset         = 0
    _name           = None
    _mtime          = None
    _real_size      = 0
    _stored_size    = 0

    def __init__(self, bigfile):
        self._bigfile = bigfile

    def load(self, data):
        raise NotImplemented()

    @property
    def name(self):
        return self._name

    @property
    def mtime(self):
        return self._mtime

    @property
    def is_compressed(self):
        return self.real_size > self.stored_size

    @property
    def real_size(self):
        return self._real_size

    @property
    def stored_size(self):
        return self._stored_size

class BigFile(StructuredFile):
    _members        = []

    def __iter__(self):
        return iter(self.get_members())

    def __len__(self):
        return len(self._members)

    def load(self):
        super(BigFile, self).load()
        self._members = self._get_members()

    def check_format(self):
        key, member_type = self.STRUCTURE[0]
        self.seek(0)
        try:
            member_type(self)
        except Exception:
            return False
        return True

    def open_member(self, member):
        if member.is_compressed:
            return StringIO(self.COMPRESSION_ALGORITHM.decompress(
                self.read(member.stored_size)))
        else:
            return _FileInFile(self, member._offset, member.stored_size)

    def get_member(self, filename):
        for member in self.get_members():
            if member.name == filename:
                return member
        else:
            raise KeyError()

    def get_members(self):
        return self._members

    def get_filenames(self):
        return [member.name for member in self.get_members()]

    def extract(self, member, path=''):
        full_filename = os.path.join(path, member.name)
        try:
            os.makedirs(os.path.dirname(full_filename))
        except os.error:
            # leaf dir already exists (probably)
            pass
        with self.open_member(member) as infile:
            with open(os.path.join(path, member.name), 'w') as outfile:
                outfile.write(infile.read())

    def extract_all(self, members=None, path=''):
        if members is None:
            members = self.get_members()
        for member in members:
            self.extract(member, path)

    def add(self, filename): pass
    def add_file(self, fileobj): pass

    def _get_members(self):
        raise NotImplemented()

class BigSection(StructuredFileSection): pass
class BigSequence(StructuredFileSequence): pass

class GearboxEncryptedBigFile(BigFile):
    MASTER_KEY                  = None
    ENCRYPTION_KEY_MARKER       = 0x00000000
    ENCRYPTION_KEY_MAX_SIZE     = 1024 # 0x0400

    _crypto                     = None

    @property
    def data_size(self):
        return self._crypto._data_size

    def load(self):
        self._crypto = self._load_encryption()
        super(GearboxEncryptedBigFile, self).load()

    def check_format(self):
        try:
            self._crypto = self._load_encryption()
        except Exception:
            return False
        return super(GearboxEncryptedBigFile, self).check_format()

    def read(self, size=None):
        if self.data_size is None:
            # we don't have the key yet, just pass through
            return self._handle.read(size)
        else:
            cur_pos = self._handle.tell()
            if cur_pos < self.data_size:
                # we're gonna read encrypted data
                if size is None:
                    # make sure we don't read past the encrypted data
                    size = self.data_size - cur_pos
                else:
                    if cur_pos + size > self.data_size:
                        raise IOError('Attempted to read past end of encryption')
                return self._read_encrypted(size)
            else:
                return self._handle.read(size)

    def _read_encrypted(self, size):
        offset = self.tell()
        return self._crypto.decrypt(self._handle.read(size), offset)

    def _load_encryption(self):
        self.seek(-4, os.SEEK_END)
        last_int_loc = self.tell()
        marker_offset = struct.unpack('<L', self._handle.read(4))[0]
        if marker_offset < (last_int_loc - 6):
            self.seek(-marker_offset, os.SEEK_CUR)
            encrypted_data_size = self.tell()
            marker = struct.unpack('<L', self._handle.read(4))[0]
            if marker == self.ENCRYPTION_KEY_MARKER:
                encryption_key_bytes = struct.unpack('<H', self._handle.read(2))[0]
                if encryption_key_bytes <= self.ENCRYPTION_KEY_MAX_SIZE:
                    local_encryption_key = bytearray(self._handle.read(encryption_key_bytes))
                    return GearboxCrypt(encrypted_data_size, local_encryption_key, self.MASTER_KEY)
                else:
                    raise GearboxEncryptionException('Invalid encryption key size: %d > %d' %
                        (encryption_key_bytes, self.ENCRYPTION_KEY_MAX_SIZE))
            else:
                raise GearboxEncryptionException('Unexpected marker value: 0x%08X should be 0x%08X' %
                    (marker, self.ENCRYPTION_KEY_MARKER))
        else:
            raise GearboxEncryptionException('Invalid marker offset: %d', marker_offset)
