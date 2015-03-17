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


import datetime
import os.path

from naabal.errors import BigFormatException
from naabal.util import timestamp_to_datetime, datetime_to_timestamp
from naabal.util.lzss import LZSSDecompressor
from naabal.formats import StructuredFileSequence
from naabal.formats.big import BigFile, BigSection, BigSequence, BigInfo


class HomeworldBigHeader(BigSection):
    MAX_TOC_ENTRIES     = 65535 # completely arbitrary
    STRUCTURE           = [
        {   # format identifier
            'key':      'magic_cookie',
            'fmt':      'c',
            'len':      7,
            'default':  'RBF1.23', # 0x524246312E3233
            'read':     lambda v: ''.join(v[:7]),
            'write':    lambda v: str(v)[:7],
        },
        {   # number of toc entries
            'key':      'toc_entry_count',
            'fmt':      'L',
            'len':      1,
            'default':  0,
            'read':     int,
            'write':    int,
        },
        {   # whether the toc is sorted or not, should always be true (0x01)
            'key':      'toc_sorted_flag',
            'fmt':      'L',
            'len':      1,
            'default':  True,
            'read':     bool,
            'write':    lambda v: 0x01 if v else 0x00,
        },
    ]

    def check(self):
        if self['magic_cookie'] != 'RBF1.23':
            raise BigFormatException('Incorrect magic cookie: %s' % self['magic_cookie'])
        if self['toc_entry_count'] < 0 or self['toc_entry_count'] > self.MAX_TOC_ENTRIES:
            raise BigFormatException('Invalid ToC entry count: %d' % self['toc_entry_count'])
        if not self['toc_sorted_flag']:
            raise BigFormatException('ToC sorted flag not set')
        return True

class HomeworldBigTocEntry(BigSection):
    MAX_FILENAME_LEN    = 128 # per src/Game/bigfile.h:78
    STRUCTURE           = [
        {   # high bits of the name CRC
            'key':      'name_crc_start',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {   # low bits of the name CRC
            'key':      'name_crc_end',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {   # length of the file name, note there is a null byte that is not included
            'key':      'name_length',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'data_stored_size',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'data_real_size',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {   # offset for beginning of name+data
            'key':      'entry_offset',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {   # timestamp of the entry (originally a time_t)
            'key':      'timestamp',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     timestamp_to_datetime,
            'write':    datetime_to_timestamp,
        },
        {   # flag for if the entry data is compressed, should match data_stored_size < data_real_size
            'key':      'compression_flag',
            'fmt':      'B',
            'len':      1,
            'default':  False,
            'read':     bool,
            'write':    lambda v: 0x01 if v else 0x00,
        },
        {   # compiler-added padding, not used for anything
            'key':      'padding1',
            'fmt':      'c',
            'len':      3,
            'default':  '\xC9\xCA\xCB',
            'read':     lambda v: ''.join(v[:3]),
            'write':    lambda v: str(v)[:3],
        },
    ]

    def check(self):
        if self['name_crc_start'] < 0 or self['name_crc_start'] > 0xFFFFFFFF:
            raise BigFormatException('Invalid value for CRC-start: %x' % self['name_crc_start'])
        if self['name_crc_end'] < 0 or self['name_crc_end'] > 0xFFFFFFFF:
            raise BigFormatException('Invalid value for CRC-end: %x' % self['name_crc_end'])
        if self['name_length'] > self.MAX_FILENAME_LEN:
            raise BigFormatException('Filename length too long: %d' % self['name_length'])
        if self['data_stored_size'] > self['data_real_size']:
            raise BigFormatException('Stored data size is larger than real size by %d bytes' %
                (self['data_stored_size'] - self['data_real_size']))
        if self['timestamp'] > datetime.datetime.utcnow():
            raise BigFormatException('Invalid timestamp: %s' % self['timestamp'])
        if self['compression_flag'] is not (self['data_stored_size'] < self['data_real_size']):
            raise BigFormatException('Data compression flag does not match data sizes: %s != (%d < %d)' %
                (self['compression_flag'], self['data_stored_size'], self['data_real_size']))
        return True

class HomeworldBigToc(BigSequence):
    CHILD_TYPE      = HomeworldBigTocEntry

    def _get_expected_length(self, handle):
        return handle._data['header']['toc_entry_count']

class HomeworldBigInfo(BigInfo):
    def load(self, data):
        self._offset        = data['entry_offset'] + data['name_length'] + 1
        self._name          = self._bigfile._read_filename(data)
        self._mtime         = data['timestamp']
        self._real_size     = data['data_real_size']
        self._stored_size   = data['data_stored_size']

class HomeworldBigFile(BigFile):
    STRUCTURE       = [
        ('header',              HomeworldBigHeader),
        ('table_of_contents',   HomeworldBigToc),
    ]

    MIN_COMPRESSION_RATIO       = 0.950
    COMPRESSION_ALGORITHM       = LZSSDecompressor()

    def _read_filename(self, toc_entry):
        self.seek(toc_entry['entry_offset'])
        filename = self.read(toc_entry['name_length'] + 1)[:-1] # skip the null byte
        filename = self._decode_filename(filename)
        filename = self._normalize_filename(filename)
        return filename

    def _decode_filename(self, filename):
        char_mask = 0xD5        # Game/bigfile.c:530 of HW1 source
        decrypted_chars = []
        for char in filename:
            char_mask = char_mask ^ ord(char)
            decrypted_chars.append(chr(char_mask))
        return ''.join(decrypted_chars)

    def _normalize_filename(self, filename):
        filename = os.path.join(*filename.split('\\'))
        return filename

    def _get_members(self):
        members = []
        for toc_entry in self._data['table_of_contents']:
            member = HomeworldBigInfo(self)
            member.load(toc_entry)
            members.append(member)
        return members
