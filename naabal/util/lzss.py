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
from cStringIO import StringIO

from naabal.util.bitio import BitReader


class LZSSCompressor(object):
    INDEX_BIT_COUNT         = 12
    LENGTH_BIT_COUNT        = 4
    WINDOW_SIZE             = 1 << INDEX_BIT_COUNT
    RAW_LOOK_AHEAD_SIZE     = 1 << LENGTH_BIT_COUNT
    BREAK_EVEN              = (1 + INDEX_BIT_COUNT + LENGTH_BIT_COUNT) / 9
    LOOK_AHEAD_SIZE         = RAW_LOOK_AHEAD_SIZE + BREAK_EVEN
    TREE_ROOT               = WINDOW_SIZE
    END_OF_STREAM           = 0
    UNUSED                  = 0
    MOD_WINDOW              = lambda s, a: a & (s.WINDOW_SIZE - 1)

    def compress(self, data):
        pass

class LZSSDecompressor(LZSSCompressor):
    def decompress(self, data):
        data_handle = StringIO(data)
        output_data = []
        current_position = 1
        match_length = None
        match_position = None
        c = None
        window = [self.UNUSED] * self.WINDOW_SIZE

        bit_reader = BitReader(data_handle)

        while True:
            if bit_reader.readbit():

                c = bit_reader.readbits(8)
                output_data.append(chr(c))
                window[current_position] = c
                current_position = self.MOD_WINDOW(current_position+1)
            else:
                match_position = bit_reader.readbits(self.INDEX_BIT_COUNT)
                if match_position == self.END_OF_STREAM:
                    break
                match_length = bit_reader.readbits(self.LENGTH_BIT_COUNT)
                match_length += self.BREAK_EVEN
                for i in xrange(match_length+1):
                    c = window[self.MOD_WINDOW(match_position+i)]
                    output_data.append(chr(c))
                    window[current_position] = c
                    current_position = self.MOD_WINDOW(current_position+1)
        return ''.join(output_data)


def decompress(data):
    return LZSSDecompressor().decompress(data)

def compress(data):
    return LZSSCompressor().compress(data)
