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

import os.path
import hashlib
import logging

from naabal.errors import BigFormatException
from naabal.formats.big import BigSection, BigFile, BigSequence, BigInfo
from naabal.util import crc32, datetime_to_timestamp, timestamp_to_datetime, \
    pad_null_string, trim_null_string
from naabal.util.zlib_wrapper import ZLIB
from naabal.util.file_io import FileInFile, chunked_copy
from naabal.util.keys import RELIC_HW2_TOOL_SECURITY_KEY, RELIC_HW2_ROOT_SECURITY_KEY

logger = logging.getLogger('naabal.formats.big.hw2')

MAX_FILENAME_LENGTH             = 256


class Homeworld2BigArchiveHeader(BigSection):
    STRUCTURE = [
        {
            'key':      'magic_cookie',
            'fmt':      '8s',
            'len':      1,
            'default':  '_ARCHIVE',
            'read':     str,
            'write':    str,
        },
        {
            'key':      'version',
            'fmt':      'L',
            'len':      1,
            'default':  0x02,
            'read':     int,
            'write':    int,
        },
        {   # hash of the tool security key and rest of the file excluding this header
            'key':      'tool_key_hash',
            'fmt':      'c',
            'len':      16,
            'default':  '\x00' * 16,
            'read':     lambda v: ''.join(v[:16]),
            'write':    lambda v: str(v)[:16],
        },
        {
            'key':      'archive_name',
            'fmt':      '128s',
            'len':      1,
            'default':  'DataArchive',
            'read':     lambda v: trim_null_string(v.decode('UTF-16-LE')),
            'write':    lambda v: pad_null_string(v, 128).encode('UTF-16-LE'),
        },
        {   # hash of the root security key and the section header + section data
            'key':      'root_key_hash',
            'fmt':      'c',
            'len':      16,
            'default':  '\x00' * 16,
            'read':     lambda v: ''.join(v[:16]),
            'write':    lambda v: str(v)[:16],
        },
        {
            'key':      'section_header_size',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'file_data_offset',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
    ]

    def check(self):
        if self['magic_cookie'] != '_ARCHIVE':
            raise BigFormatException('Incorrect magic cookie: %s' % self['magic_cookie'])
        return True

class Homeworld2BigSectionHeader(BigSection):
    STRUCTURE = [
        {
            'key':      'toc_list_offset',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'toc_list_count',
            'fmt':      'H',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'folder_list_offset',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'folder_list_count',
            'fmt':      'H',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'file_info_list_offset',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'file_info_list_count',
            'fmt':      'H',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'filename_list_offset',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'filename_list_count',
            'fmt':      'H',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
    ]

class Homeworld2BigTocEntry(BigSection):
    STRUCTURE = [
        {
            'key':      'namespace',
            'fmt':      '64s',
            'len':      1,
            'default':  '',
            'read':     trim_null_string,
            'write':    lambda v: pad_null_string(v, 64),
        },
        {
            'key':      'filename',
            'fmt':      '64s',
            'len':      1,
            'default':  '',
            'read':     trim_null_string,
            'write':    lambda v: pad_null_string(v, 64),
        },
        {
            'key':      'first_folder_idx',
            'fmt':      'H',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'last_folder_idx',
            'fmt':      'H',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'first_fileinfo_idx',
            'fmt':      'H',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'last_fileinfo_idx',
            'fmt':      'H',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'start_folder_idx',
            'fmt':      'H',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
    ]

class Homeworld2BigToc(BigSequence):
    CHILD_TYPE      = Homeworld2BigTocEntry

    def _get_expected_length(self, handle):
        return handle._data['section_header']['toc_list_count']

class Homeworld2BigFolderEntry(BigSection):
    STRUCTURE = [
        {
            'key':      'filename_offset',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'first_subfolder_idx',
            'fmt':      'H',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'last_subfolder_idx',
            'fmt':      'H',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'first_fileinfo_idx',
            'fmt':      'H',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'last_fileinfo_idx',
            'fmt':      'H',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
    ]

class Homeworld2BigFolderList(BigSequence):
    CHILD_TYPE      = Homeworld2BigFolderEntry

    def _get_expected_length(self, handle):
        return handle._data['section_header']['folder_list_count']

class Homeworld2BigFileInfoEntry(BigSection):
    STRUCTURE = [
        {
            'key':      'filename_offset',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'compression_flag',
            'fmt':      'B',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'file_data_offset',
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
    ]

class Homeworld2BigFileInfoList(BigSequence):
    CHILD_TYPE      = Homeworld2BigFileInfoEntry

    def _get_expected_length(self, handle):
        return handle._data['section_header']['file_info_list_count']

class Homeworld2BigFileEntry(BigSection):
    STRUCTURE = [
        {
            'key':      'filename',
            'fmt':      str(MAX_FILENAME_LENGTH)+'s',
            'len':      1,
            'default':  '',
            'read':     trim_null_string,
            'write':    lambda v: pad_null_string(v, MAX_FILENAME_LENGTH),
        },
        {
            'key':      'timestamp',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     timestamp_to_datetime,
            'write':    datetime_to_timestamp,
        },
        {
            'key':      'crc32',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
    ]

class Homeworld2BigFileEntryList(BigSequence):
    CHILD_TYPE      = Homeworld2BigFileEntry

    def _get_expected_length(self, handle):
        return handle._data['section_header']['filename_list_count']

class Homeworld2BigInfo(BigInfo):
    def load(self, data):
        metadata = self._bigfile._get_file_metadata(data)
        self._offset        = self._bigfile._get_file_data_offset(data)
        self._name          = self._bigfile._get_full_filename(data)
        self._mtime         = metadata['timestamp']
        self._real_size     = data['data_real_size']
        self._stored_size   = data['data_stored_size']

class Homeworld2BigFile(BigFile):
    STRUCTURE           = [
        ('archive_header',          Homeworld2BigArchiveHeader),
        ('section_header',          Homeworld2BigSectionHeader),
        ('table_of_contents',       Homeworld2BigToc),
        ('folders',                 Homeworld2BigFolderList),
        ('file_info',               Homeworld2BigFileInfoList),
    ]

    ROOT_KEY                    = RELIC_HW2_ROOT_SECURITY_KEY
    TOOL_KEY                    = RELIC_HW2_TOOL_SECURITY_KEY
    COMPRESSION_ALGORITHM       = ZLIB()
    MIN_BATCH_COMPRESSION_SIZE  = 4 * 1024 # 4KB

    def _get_members(self):
        self._filename_map = self._build_filename_map()
        members = []
        for file_info in self._data['file_info']:
            member = Homeworld2BigInfo(self)
            member.load(file_info)
            members.append(member)
        return members

    def _build_filename_map(self):
        fn_map = [None] * len(self._data['file_info'])
        for fn, fi in self._walk_contents():
            fn_map[self._data['file_info']._data_list.index(fi)] = fn
        return fn_map

    def _read_filename(self, file_info_entry):
        self.seek(self._get_filename_offset(file_info_entry))
        filename = self.read(MAX_FILENAME_LENGTH).split('\x00', 1)[0]
        filename = self._normalize_filename(filename)
        return filename

    def _normalize_filename(self, filename):
        return os.path.join(*filename.split('\\'))

    def _walk_contents(self):
        for toc_entry in self._data['table_of_contents']:
            for item_path, item in self._walk_folder(self._data['folders'][toc_entry['start_folder_idx']]):
                yield os.path.join(toc_entry['filename'], item_path), item

    def _walk_folder(self, folder_entry):
        folder_name = self._read_filename(folder_entry) or ''
        if folder_entry['first_subfolder_idx'] != folder_entry['last_subfolder_idx']:
            for subfolder in self._data['folders'][folder_entry['first_subfolder_idx']:folder_entry['last_subfolder_idx']]:
                for item_path, item in self._walk_folder(subfolder):
                    yield item_path, item
        for file_info in self._data['file_info'][folder_entry['first_fileinfo_idx']:folder_entry['last_fileinfo_idx']]:
            yield os.path.join(folder_name, self._read_filename(file_info)), file_info

    def _get_file_data_offset(self, file_info_entry):
        return self._data['archive_header']['file_data_offset'] + file_info_entry['file_data_offset']

    def _get_filename_offset(self, entry):
        return Homeworld2BigArchiveHeader.data_size + \
            self._data['section_header']['filename_list_offset'] + \
            entry['filename_offset']

    def _get_file_metadata(self, file_info_entry):
        self.seek(self._get_file_data_offset(file_info_entry) - Homeworld2BigFileEntry.data_size)
        file_metadata = Homeworld2BigFileEntry(self)
        return file_metadata

    def _get_full_filename(self, file_info_entry):
        return self._filename_map[self._data['file_info']._data_list.index(file_info_entry)]

    def _get_tool_key_hash(self):
        md5_hash = hashlib.md5(self.TOOL_KEY)
        self.seek(self['archive_header'].data_size)
        chunked_copy(self.read, md5_hash.update)
        logger.debug('Calculated tool key hash as: %s', md5_hash.hexdigest())
        return md5_hash.digest()

    def _get_root_key_hash(self):
        md5_hash = hashlib.md5(self.ROOT_KEY)
        data_handle = FileInFile(self, self['archive_header'].data_size,
            size=self['archive_header']['file_data_offset'] - self['archive_header'].data_size)
        chunked_copy(data_handle.read, md5_hash.update)
        logger.debug('Calculated root key hash as: %s', md5_hash.hexdigest())
        return md5_hash.digest()
