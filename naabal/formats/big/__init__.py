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

from naabal.formats import StructuredFile, StructuredFileSection, StructuredFileSequence
from naabal.errors import GearboxEncryptionException


class BigFile(StructuredFile): pass
class BigSection(StructuredFileSection): pass
class BigSequence(StructuredFileSequence): pass

class GearboxEncryptedBigFile(BigFile):
    MASTER_KEY                  = None
    ENCRYPTION_KEY_MARKER       = 0x00000000
    ENCRYPTION_KEY_MAX_SIZE     = 1024

    _encrypted_data_size        = None
    _encryption_key             = None

    def populate(self):
        self._load_encryption_key()
        super(GearboxEncryptedBigFile, self).populate()

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
                    size = cur_pos - self._encrypted_data_size
                else:
                    if cur_pos + size > self._encrypted_data_size:
                        raise IOError('Attempted to read past end of encryption')
                return self._read_encrypted(size)
            else:
                return self._handle.read(size)

    def _read_encrypted(self, size):
        key_size = len(self._encryption_key)
        key_offset = self.tell() % key_size
        encrypted_data = self._handle.read(size)
        decrypted_data = ''.join(chr(self._encryption_key[(key_offset + i) % key_size]) \
            for i, c in zip(range(len(encrypted_data)), encrypted_data))
        if decrypted_data[:8] != '_ARCHIVE':
            raise Exception('Decryption failed: %s -> %s' % (encrypted_data[:8], decrypted_data[:8]))
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
                encryption_key_size = struct.unpack('<H', self._handle.read(2))[0]
                if encryption_key_size <= self.ENCRYPTION_KEY_MAX_SIZE:
                    self._encrypted_data_size = encrypted_data_size
                    local_encryption_key = bytearray(self._handle.read(encryption_key_size))
                    encryption_key = self._combine_keys(local_encryption_key, self.MASTER_KEY)
                    self._encryption_key = encryption_key
                else:
                    raise GearboxEncryptionException('Invalid encryption key size: %d > %d' %
                        (encryption_key_size, self.ENCRYPTION_KEY_MAX_SIZE))
            else:
                raise GearboxEncryptionException('Unexpected marker value: 0x%08X should be 0x%08X' %
                    (marker, self.ENCRYPTION_KEY_MARKER))
        else:
            raise GearboxEncryptionException('Invalid marker offset: %d', marker_offset)

    def _combine_keys(self, local_key, global_key):
        ROTL = lambda val, bits: ((val << bits) | (val >> (32 - bits)))
        key_size = len(local_key)
        combined_key = bytearray('\x00' * key_size)
        for i in xrange(0, key_size, 4):
            c = local_key[i/4]
            for b in range(4):
                val = ROTL(c + self._encrypted_data_size, 8)
                bytes = (
                    val & 0x000000FF,
                    (val & 0x0000FF00) >> 8,
                    (val & 0x00FF0000) >> 16,
                    (val & 0xFF000000) >> 24,
                )
                for j in range(4):
                    c = global_key[(c ^ bytes[j]) & 0xFF] ^ (c >> 8)
                combined_key[i + b] = c & 0xFF
        return combined_key
