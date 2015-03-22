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

import zlib

class ZLIB(object):
    def __init__(self, chunk_size=4 * 1024):
        self._chunk_size = chunk_size

    def compress_stream(self, input_buffer, output_buffer):
        output_buffer_pos_start = output_buffer.tell()
        worker = zlib.compressobj()
        chunk = input_buffer.read(self._chunk_size)
        while len(chunk) != 0:
            output_buffer.write(worker.compress(chunk))
            chunk = input_buffer.read(self._chunk_size)
        output_buffer.write(worker.flush())
        return output_buffer.tell() - output_buffer_pos_start

    def compress(self, input_data):
        return zlib.compress(input_data)

    def decompress_stream(self, input_buffer, output_buffer):
        output_buffer_pos_start = output_buffer.tell()
        worker = zlib.decompressobj()
        chunk = input_buffer.read(self._chunk_size)
        while len(chunk) != 0:
            output_buffer.write(worker.decompress(worker.unconsumed_tail + chunk))
            chunk = input_buffer.read(self._chunk_size)
        output_buffer.write(worker.flush())
        return output_buffer.tell() - output_buffer_pos_start

    def decompress(self, input_data):
        return zlib.decompress(input_data)

decompress = zlib.decompress
compress = zlib.compress
