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
from naabal.util import timestamp_to_datetime, datetime_to_timestamp, crc32
from naabal.util.lzss import LZSS
from naabal.util.file_io import chunked_copy
from naabal.formats import StructuredFileSequence
from naabal.formats.big import BigFile, BigSection, BigSequence, BigInfo


A_YEAR_IN_THE_FUTURE = datetime.datetime.utcnow() + datetime.timedelta(365)

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
        if self['timestamp'] > A_YEAR_IN_THE_FUTURE:
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
    COMPRESSION_ALGORITHM       = LZSS()

    def _read_filename(self, toc_entry):
        self.seek(toc_entry['entry_offset'])
        filename = self.read(toc_entry['name_length'] + 1)[:-1] # skip the null byte
        filename = self._decode_filename(filename)
        filename = self._normalize_filename(filename)
        return filename

    def _decode_filename(self, filename):
        encoded_filename = bytearray(filename)
        decoded_filename = bytearray(len(filename) + 1)
        decoded_filename[0] = 0xD5 # Game/bigfile.c:530 of HW1 source
        for i, byte in enumerate(encoded_filename):
            decoded_filename[i+1] = decoded_filename[i] ^ byte
        return str(decoded_filename[1:])

    def _encode_filename(self, filename):
        maskch = 0xD5
        filename = bytearray(filename)

        for i in range(len(filename)):
            nextmask = filename[i]
            filename[i] ^= maskch
            maskch = nextmask

        return str(filename)

    def _normalize_filename(self, filename):
        filename = os.path.join(*filename.split('\\'))
        filename = os.path.normpath(filename)
        return filename

    def _denormalize_filename(self, filename):
        filename = os.path.normpath(filename)
        filename = '\\'.join(filename.split(os.sep))
        return filename

    def _get_filename_crcs(self, decoded_filename):
        """Compute the CRC32 checksums of the first and last halves of the un-encoded
        (but not normalized) filename.

        NOTE: There is an intentionally un-fixed bug, if the filename length is odd
        then the last character is not included in the latter half checksum. Can't
        fix it without breaking compatibility
        """

        decoded_filename = decoded_filename.lower()
        half_len = len(decoded_filename) / 2
        return (crc32(decoded_filename[:half_len]), crc32(decoded_filename[half_len:half_len*2]))

    def _get_members(self):
        members = []
        for toc_entry in self._data['table_of_contents']:
            member = HomeworldBigInfo(self)
            member.load(toc_entry)
            members.append(member)
        return members

    def save(self):
        crc_fix = lambda crc_start, crc_end: (crc_start << 32) | crc_end

        sorted_members = sorted(self.get_members(), key=lambda m: \
            crc_fix(*self._get_filename_crcs(self._denormalize_filename(m.name))))
        member_count = len(sorted_members)
        self['header']['toc_entry_count'] = len(sorted_members)
        self['table_of_contents']._data_list = [self['table_of_contents'].CHILD_TYPE() \
            for i in range(member_count)]

        offset = self['header'].data_size + (len(sorted_members) * self['table_of_contents'].CHILD_TYPE.data_size)

        max_data_size = sum(len(m.name) + 1 + m.real_size for m in sorted_members)
        max_file_size = offset + max_data_size

        self.truncate(max_file_size)

        for i, member in enumerate(sorted_members):
            crc_head, crc_tail = self._get_filename_crcs(self._denormalize_filename(member.name))
            toc_entry = self['table_of_contents'][i]
            toc_entry['name_crc_start'] = crc_head
            toc_entry['name_crc_end'] = crc_tail
            toc_entry['name_length'] = len(member.name)
            toc_entry['data_real_size'] = member.real_size
            toc_entry['data_stored_size'] = member.stored_size
            toc_entry['timestamp'] = member.mtime
            toc_entry['entry_offset'] = offset

            self.seek(offset)
            self.write(self._encode_filename(self._denormalize_filename(member.name)) + '\x00')

            data_offset = self.tell()
            member_handle = member.open()
            self.COMPRESSION_ALGORITHM.compress_stream(member_handle, self)
            stored_size = self.tell() - data_offset
            if (float(stored_size) / float(member.real_size)) < self.MIN_COMPRESSION_RATIO:
                toc_entry['data_stored_size'] = stored_size
                member._stored_size = stored_size
            else:
                self.seek(data_offset)
                member_handle.seek(0)
                chunked_copy(member_handle.read, self.write)

            toc_entry['compression_flag'] = member.is_compressed
            offset += len(member.name) + 1 + member.stored_size
            print 'Added file {2:4d}/{3:4d} [{0:8d} b]: {1}'.format(
                member.stored_size, member.name, i + 1, member_count)

        # cut the file off at the end of the data we wrote
        self.truncate(offset)

        # write the header + toc
        super(HomeworldBigFile, self).save()
