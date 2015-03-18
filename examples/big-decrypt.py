#/usr/bin/env python
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


from naabal.formats.big.hwrm import HomeworldRemasteredBigFile

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='big-decrypt.py',
        description='Extract contents of a .big file to a directory')
    parser.add_argument('-c', '--chunk-size', type=int, default=1024 * 4)
    parser.add_argument('src_filename')
    parser.add_argument('dest_filename')
    args = parser.parse_args()

    with HomeworldRemasteredBigFile(args.src_filename) as infile:
        bigfile.load()
        with open(args.dest_filename, 'w') as outfile:
            chunk_size = args.chunk_size
            data_size = infile.data_size
            for i in xrange(0, data_size, chunk_size):
                outfile.write(infile.read(chunk_size))
