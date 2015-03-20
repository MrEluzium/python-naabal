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

__all__ = ['decompress', 'compress', 'LZSSCompressor', 'LZSSDecompressor']

import struct
from cStringIO import StringIO

from naabal.util.bitio import BitReader, BitWriter


MOD_WINDOW = lambda value: value & (LZSS.WINDOW_SIZE - 1)


class LZSS(object):
    INDEX_BIT_COUNT         = 12
    LENGTH_BIT_COUNT        = 4
    WINDOW_SIZE             = 1 << INDEX_BIT_COUNT # 4096
    RAW_LOOK_AHEAD_SIZE     = 1 << LENGTH_BIT_COUNT # 16
    BREAK_EVEN              = (1 + INDEX_BIT_COUNT + LENGTH_BIT_COUNT) / 9 # 1
    LOOK_AHEAD_SIZE         = RAW_LOOK_AHEAD_SIZE + BREAK_EVEN
    TREE_ROOT               = WINDOW_SIZE
    END_OF_STREAM           = 0x000
    UNUSED                  = 0

    def __init__(self, handle):
        self._buffer = handle
        self._buffer_size = self._get_buffer_size()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        pass

    def _get_buffer_size(self):
        prev_pos =  self._buffer.tell()
        self._buffer.seek(0, 2) # EOF
        size = self._buffer.tell()
        self._buffer.seek(prev_pos)
        return size

class LZSSCompressor(LZSS):
    def compress_stream(self, output_buffer=None):
        if output_buffer is None:
            output_buffer = StringIO()

        current_position    = 1
        match_length        = 0
        match_position      = 0
        window = bytearray(self.WINDOW_SIZE)

        for i in xrange(self.LOOK_AHEAD_SIZE):
            c = self._buffer.read(1)
            if len(c) == 0:
                break
            window[current_position + i] = ord(c)

        look_ahead_bytes = i + 1
        tree = _LZSSTree(current_position, window)

        with BitWriter(output_buffer) as bit_writer:
            while look_ahead_bytes > 0:
                if match_length > look_ahead_bytes:
                    match_length = look_ahead_bytes

                if match_length <= self.BREAK_EVEN:
                    replace_count = 1
                    bit_writer.write_bit(1)
                    bit_writer.write_bits(window[current_position], 8)
                else:
                    bit_writer.write_bit(0)
                    bit_writer.write_bits(match_position, self.INDEX_BIT_COUNT)
                    bit_writer.write_bits(match_length - (self.BREAK_EVEN + 1), self.LENGTH_BIT_COUNT)
                    replace_count = match_length

                for i in xrange(replace_count):
                    tree.delete_string(MOD_WINDOW(current_position + self.LOOK_AHEAD_SIZE))
                    c = self._buffer.read(1)

                    if len(c) == 0:
                        look_ahead_bytes -= 1
                    else:
                        window[MOD_WINDOW(current_position + self.LOOK_AHEAD_SIZE)] = ord(c)

                    current_position = MOD_WINDOW(current_position + 1)
                    if look_ahead_bytes:
                        match_length, match_position = tree.add_string(current_position, match_position)

            bit_writer.write_bit(0)
            bit_writer.write_bits(self.END_OF_STREAM, self.INDEX_BIT_COUNT)

        return output_buffer

    def compress(self):
        handle = self.compress_stream()
        return handle.getvalue()

class LZSSDecompressor(LZSS):
    def decompress_stream(self, output_buffer=None):
        if output_buffer is None:
            output_buffer = StringIO()

        current_position = 1
        window = bytearray(self.WINDOW_SIZE)

        with BitReader(self._buffer) as bit_reader:
            while True:
                pass_through = bit_reader.read_bit()
                if pass_through:
                    c = bit_reader.read_bits(8)
                    output_buffer.write(chr(c))
                    window[current_position] = c
                    current_position = MOD_WINDOW(current_position + 1)
                else:
                    match_position = bit_reader.read_bits(self.INDEX_BIT_COUNT)
                    if match_position == self.END_OF_STREAM:
                        break
                    match_length = bit_reader.read_bits(self.LENGTH_BIT_COUNT)
                    match_length += self.BREAK_EVEN

                    for i in xrange(match_length + 1):
                        c = window[MOD_WINDOW(match_position + i)]
                        output_buffer.write(chr(c))
                        window[current_position] = c
                        current_position = MOD_WINDOW(current_position + 1)

        return output_buffer

    def decompress(self):
        handle = self.decompress_stream()
        return handle.getvalue()

def decompress(data):
    return LZSSDecompressor(StringIO(data)).decompress()

def compress(data):
    return LZSSCompressor(StringIO(data)).compress()

class _LZSSTreeNode(object):
    parent = 0
    smaller_child = 0
    larger_child = 0

    def __repr__(self):
        return '<%4d . %4d . %4d>' % (self.parent, self.larger_child, self.smaller_child)

    def copy_node(self, source_node):
        self.parent = source_node.parent
        self.smaller_child = source_node.smaller_child
        self.larger_child = source_node.larger_child

class _LZSSTree(object):
    _data = None

    def __init__(self, root_idx, window):
        self._window = window
        self._data = [_LZSSTreeNode() for i in xrange(LZSS.WINDOW_SIZE + 1)]
        self[LZSS.TREE_ROOT].larger_child = root_idx
        self[root_idx].parent = LZSS.TREE_ROOT
        self[root_idx].larger_child = LZSS.UNUSED
        self[root_idx].smaller_child = LZSS.UNUSED

    def __repr__(self):
        return repr(self._data)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def contract_node(self, old_node, new_node):
        self[new_node].parent = self[old_node].parent
        if self[self[old_node].parent].larger_child == old_node:
            self[self[old_node].parent].larger_child = new_node
        else:
            self[self[old_node].parent].smaller_child = new_node
        self[old_node].parent = LZSS.UNUSED

    def replace_node(self, old_node, new_node):
        parent = self[old_node].parent

        if self[parent].smaller_child == old_node:
            self[parent].smaller_child = new_node
        else:
            self[parent].larger_child = new_node

        self[new_node].copy_node(self[old_node])
        self[self[new_node].smaller_child].parent = new_node
        self[self[new_node].larger_child].parent = new_node
        self[old_node].parent = LZSS.UNUSED

    def find_next_node(self, node):
        next = self[node].smaller_child
        while self[next].larger_child != LZSS.UNUSED:
            next = self[next].larger_child
        return next

    def delete_string(self, p):
        if self[p].parent == LZSS.UNUSED:
            return

        if self[p].larger_child == LZSS.UNUSED:
            self.contract_node(p, self[p].smaller_child)
        elif self[p].smaller_child == LZSS.UNUSED:
            self.contract_node(p, self[p].larger_child)
        else:
            replacement = self.find_next_node(p)
            self.delete_string(replacement)
            self.replace_node(p, replacement)

    def add_string(self, new_node, match_position):
        if new_node == LZSS.END_OF_STREAM:
            return (0, match_position)

        test_node = self[LZSS.TREE_ROOT].larger_child
        match_length = 0

        while True:
            for i in xrange(LZSS.LOOK_AHEAD_SIZE):
                delta = self._window[MOD_WINDOW(new_node + i)] - \
                    self._window[MOD_WINDOW(test_node + i)]
                if delta != 0:
                    break

            if i >= match_length:
                match_length = i
                match_position = test_node
                if match_length >= LZSS.LOOK_AHEAD_SIZE:
                    self.replace_node(test_node, new_node)
                    return (match_length, match_position)

            if delta >= 0:
                child_attr = 'larger_child'
            else:
                child_attr = 'smaller_child'

            if getattr(self[test_node], child_attr) == LZSS.UNUSED:
                setattr(self[test_node], child_attr, new_node)
                self[new_node].parent = test_node
                self[new_node].larger_child = LZSS.UNUSED
                self[new_node].smaller_child = LZSS.UNUSED
                return (match_length, match_position)

            test_node = getattr(self[test_node], child_attr)
