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
from naabal.util.lzss import LZSSDecompressor
from naabal.formats.big import BigFile, BigSection


class HomeworldBigHeader(BigSection):
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
        if self['toc_entry_count'] < 0 or self['toc_entry_count'] > 20000: #arbitrary
            raise BigFormatException('Invalid ToC entry count: %d' % self['toc_entry_count'])
        if not self['toc_sorted_flag']:
            raise BigFormatException('ToC sorted flag not set')
        return True

class HomeworldBigTocEntry(BigSection):
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
            'read':     lambda v: datetime.datetime.utcfromtimestamp(float(v)),
            'write':    int,
        },
        {   # flag for if the entry data is compressed, should match data_stored_size < data_real_size
            'key':      'data_compressed_flag',
            'fmt':      'B',
            'len':      1,
            'default':  False,
            'read':     bool,
            'write':    lambda v: 0x01 if v else 0x00,
        },
        {   # compiler-added padding, not used for anything
            'key':      'padding',
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
        if self['name_length'] > 128:
            raise BigFormatException('Filename length too long: %d' % self['name_length'])
        if self['data_stored_size'] > self['data_real_size']:
            raise BigFormatException('Stored data size is larger than real size by %d bytes' %
                (self['data_stored_size'] - self['data_real_size']))
        if self['timestamp'] > datetime.datetime.now():
            raise BigFormatException('Invalid timestamp: %s' % self['timestamp'])
        if self['data_compressed_flag'] is not (self['data_stored_size'] < self['data_real_size']):
            raise BigFormatException('Data compression flag does not match data sizes')
        return True

class HomeworldBigFile(BigFile):
    MIN_COMPRESSION_RATIO       = 0.950

    HEADER_CLASS    = HomeworldBigHeader
    TOC_ENTRY_CLASS = HomeworldBigTocEntry

    header          = None
    toc_entries     = []

    _lzss           = LZSSDecompressor()

    def __init__(self, filename, mode='r'):
        super(HomeworldBigFile, self).__init__(filename, mode)
        self.header = self.HEADER_CLASS()
        self.header.populate(self._handle.read(self.header.data_size))

        self.toc_entries = [self.TOC_ENTRY_CLASS(self._handle.read(self.TOC_ENTRY_CLASS.data_size)) \
            for i in xrange(self.header['toc_entry_count'])]

    def __iter__(self):
        return (entry for entry in self.toc_entries)

    def get_filename(self, toc_entry):
        self._handle.seek(toc_entry['entry_offset'])
        filename = self._handle.read(toc_entry['name_length'] + 1)[:-1] # skip the null byte
        filename = self._decrypt_filename(filename)
        filename = os.path.join(*filename.split('\\'))
        return filename

    def get_data(self, toc_entry):
        self._handle.seek(toc_entry['entry_offset'] + toc_entry['name_length'] + 1)
        file_data = self._handle.read(toc_entry['data_stored_size'])
        if toc_entry['data_compressed_flag']:
            return self._lzss.decompress(file_data)
        else:
            return file_data

    def _decrypt_filename(self, filename):
        char_mask = 0xD5        # Game/bigfile.c:530 of HW1 source
        decrypted_chars = []
        for char in filename:
            char_mask = char_mask ^ ord(char)
            decrypted_chars.append(chr(char_mask))
        return ''.join(decrypted_chars)
