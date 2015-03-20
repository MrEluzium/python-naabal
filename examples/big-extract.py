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

from naabal.util.helpers import big_open

if __name__ == '__main__':
    import argparse
    import os
    import fnmatch

    parser = argparse.ArgumentParser(prog='big-extract.py',
        description='Extract contents of a .big file to a directory')
    parser.add_argument('-i', '--include-matching')
    parser.add_argument('--no-decompress', action='store_false')
    parser.add_argument('filename')
    parser.add_argument('destination', default=os.getcwd(), nargs='?')
    args = parser.parse_args()

    with big_open(args.filename) as bigfile:
        bigfile.load()
        if args.include_matching:
            member_list = [m for m in bigfile.get_members() if fnmatch.fnmatch(m.name, args.include_matching)]
        else:
            member_list = bigfile.get_members()
        for member in member_list:
            bigfile.extract(member, args.destination, args.no_decompress)
            print 'Extracted {size:8d} bytes: {name}'.format(size=member.real_size, name=member.name)
