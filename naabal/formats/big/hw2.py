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


from naabal.formats.big import BigSection, BigFile

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
        {
            'key':      'md5_hash1',
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
            'read':     lambda v: v.decode('UTF-16-LE').replace('\x00', ''),
            'write':    lambda v: (v[:128] + ('\x00' * (128 - len(v)))).encode('UTF-16-LE'),
        },
        {
            'key':      'md5_hash2',
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
            'key':      'alias_name',
            'fmt':      '64s',
            'len':      1,
            'default':  '',
            'read':     lambda v: v.replace('\x00', ''),
            'write':    str,
        },
        {
            'key':      'name',
            'fmt':      '64s',
            'len':      1,
            'default':  '',
            'read':     lambda v: v.replace('\x00', ''),
            'write':    str,
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
            'key':      'first_filename_idx',
            'fmt':      'H',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'last_filename_idx',
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
            'key':      'first_filename_idx',
            'fmt':      'H',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'last_filename_idx',
            'fmt':      'H',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
    ]

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

class Homeworld2BigFileEntry(BigSection):
    STRUCTURE = [
        {
            'key':      'filename',
            'fmt':      '256s',
            'len':      1,
            'default':  '',
            'read':     str,
            'write':    str,
        },
        {
            'key':      'mtime',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {
            'key':      'crc',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
    ]

class Homeworld2BigFile(BigFile):
    ARCHIVE_HEADER_CLASS    = Homeworld2BigArchiveHeader
    SECTION_HEADER_CLASS    = Homeworld2BigSectionHeader
    TOC_ENTRY_CLASS         = Homeworld2BigTocEntry
    FOLDER_ENTRY_CLASS      = Homeworld2BigFolderEntry
    FILE_INFO_ENTRY_CLASS   = Homeworld2BigFileInfoEntry
    FILE_ENTRY_CLASS        = Homeworld2BigFileEntry

    header              = None
    sections            = None
    toc_entries         = []
    folder_entries      = []
    file_info_entries   = []
    file_entries        = []

    def __init__(self, filename, mode='r'):
        super(Homeworld2BigFile, self).__init__(filename, mode)
        self.header = self.ARCHIVE_HEADER_CLASS()
        self.header.populate(self._handle.read(self.header.data_size))
        self.sections = self.SECTION_HEADER_CLASS()
        self.sections.populate(self._handle.read(self.sections.data_size))
        self.toc_entries = [self.TOC_ENTRY_CLASS(self._handle.read(self.TOC_ENTRY_CLASS.data_size)) \
            for i in xrange(self.sections['toc_list_count'])]
        self.folder_entries = [self.FOLDER_ENTRY_CLASS(self._handle.read(self.FOLDER_ENTRY_CLASS.data_size)) \
            for i in xrange(self.sections['folder_list_count'])]
        self.file_info_entries = [self.FILE_INFO_ENTRY_CLASS(self._handle.read(self.FILE_INFO_ENTRY_CLASS.data_size)) \
            for i in xrange(self.sections['file_info_list_count'])]
