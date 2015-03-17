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
from tarfile import _FileInFile

from naabal.formats import StructuredFile, StructuredFileSection, StructuredFileSequence
from naabal.util import split_by
from naabal.util.c_macros import ROTL, SPLIT_TO_BYTES, CAST_TO_CHAR, COMBINE_BYTES
from naabal.errors import GearboxEncryptionException


class BigInfo(object):
    _bigfile        = None
    _offset         = 0
    _name           = None
    _mtime          = None
    _compressed     = False
    _real_size      = 0
    _stored_size    = 0
    _crc32          = 0x00

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
        return self._compressed

    @property
    def real_size(self):
        return self._real_size

    @property
    def stored_size(self):
        return self._stored_size

    @property
    def crc32(self):
        return self._crc32


class BigFile(StructuredFile):
    _members        = []

    def __iter__(self):
        return iter(self.get_members())

    def open_member(self, member):
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

    def extract(self, member, path=""):
        with self.open_member(member) as infile:
            with open(os.path.join(path, member.name), 'w') as outfile:
                outfile.write(infile.read())

    def extract_all(self, members=None, path=""):
        if members is None:
            members = self.get_members()
        for member in members:
            self.extract(member, path)

    def add(self, filename): pass
    def add_file(self, fileobj): pass

    def get_biginfo(self, filename): pass

class BigSection(StructuredFileSection): pass
class BigSequence(StructuredFileSequence): pass

class GearboxEncryptedBigFile(BigFile):
    MASTER_KEY                  = None
    ENCRYPTION_KEY_MARKER       = 0x00000000
    ENCRYPTION_KEY_MAX_SIZE     = 1024 # 0x0400

    _encrypted_data_size        = None
    _encryption_key             = None

    def load(self):
        self._load_encryption_key()
        super(GearboxEncryptedBigFile, self).load()

    def read(self, size=None):
        if self._encrypted_data_size is None:
            # we don't have the key yet, just pass through
            return self._handle.read(size)
        else:
            cur_pos = self._handle.tell()
            if cur_pos < self._encrypted_data_size:
                # we're gonna read encrypted data
                if size is None:
                    # make sure we don't read past the encrypted data
                    size = self._encrypted_data_size - cur_pos
                else:
                    if cur_pos + size > self._encrypted_data_size:
                        raise IOError('Attempted to read past end of encryption')
                return self._read_encrypted(size)
            else:
                return self._handle.read(size)

    def _read_encrypted(self, size):
        key_size = len(self._encryption_key)
        key_offset = self.tell()
        encrypted_data = bytearray(self._handle.read(size))
        decrypted_data = ''.join(chr(CAST_TO_CHAR(c + self._encryption_key[(key_offset + i) % key_size])) \
            for i, c in zip(range(len(encrypted_data)), encrypted_data))
        return decrypted_data

    def _load_encryption_key(self):
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
                    self._encrypted_data_size = encrypted_data_size
                    local_encryption_key = bytearray(self._handle.read(encryption_key_bytes))
                    encryption_key = self._combine_keys(encryption_key_bytes,
                        local_encryption_key, self.MASTER_KEY)
                    self._encryption_key = encryption_key
                else:
                    raise GearboxEncryptionException('Invalid encryption key size: %d > %d' %
                        (encryption_key_bytes, self.ENCRYPTION_KEY_MAX_SIZE))
            else:
                raise GearboxEncryptionException('Unexpected marker value: 0x%08X should be 0x%08X' %
                    (marker, self.ENCRYPTION_KEY_MARKER))
        else:
            raise GearboxEncryptionException('Invalid marker offset: %d', marker_offset)

    def _combine_keys(self, key_byte_count, local_key, global_key):
        local_key = [COMBINE_BYTES(bytes) for bytes in split_by(local_key, 4)]
        global_key = [COMBINE_BYTES(bytes) for bytes in split_by(global_key, 4)]
        combined_key = bytearray(key_byte_count)
        for i in xrange(0, key_byte_count, 4):
            c = local_key[i / 4]
            for b in range(4):
                bytes = SPLIT_TO_BYTES(ROTL(c + self._encrypted_data_size, 8))
                for j in range(4):
                    c = global_key[CAST_TO_CHAR(c ^ bytes[j])] ^ (c >> 8)
                combined_key[i + b] = CAST_TO_CHAR(c)
        return combined_key
