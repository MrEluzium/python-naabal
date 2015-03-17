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

from naabal.formats.big import GearboxEncryptedBigFile
from naabal.formats.big.hw1 import HomeworldBigHeader, HomeworldBigTocEntry, HomeworldBigFile
from naabal.formats.big.hw2 import Homeworld2BigFile
from naabal.util.keys import GEARBOX_HOMEWORLD_REMASTERED_KEY


class HomeworldClassicBigHeader(HomeworldBigHeader): pass

class HomeworldClassicBigTocEntry(HomeworldBigTocEntry):
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
            'fmt':      'H',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {   # seems to just be more padding
            'key':      'unknown1',
            'fmt':      'H',
            'len':      1,
            'default':  0xA7,
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
            'write':    int, # TODO: this needs to change a datetime to an int
        },
        {   # compiler-added padding, not used for anything
            'key':      'padding1',
            'fmt':      'L',
            'len':      1,
            'default':  0x00,
            'read':     int,
            'write':    int,
        },
        {   # flag for if the entry data is compressed, should match data_stored_size < data_real_size
            'key':      'data_compressed_flag',
            'fmt':      'L',
            'len':      1,
            'default':  False,
            'read':     bool,
            'write':    lambda v: 0x01 if v else 0x00,
        },
    ]

class HomeworldClassicBigFile(HomeworldBigFile):
    HEADER_CLASS    = HomeworldClassicBigHeader
    TOC_ENTRY_CLASS = HomeworldClassicBigTocEntry

class Homeworld2ClassicBigFile(Homeworld2BigFile): pass

class HomeworldRemasteredBigFile(GearboxEncryptedBigFile, Homeworld2BigFile):
    MASTER_KEY                      = GEARBOX_HOMEWORLD_REMASTERED_KEY
    ENCRYPTION_KEY_MARKER           = 0xDEADBE7A
