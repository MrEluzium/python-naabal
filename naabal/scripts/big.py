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

import argparse
import sys
import os
import fnmatch
import datetime

from naabal.util.helpers import big_load
from naabal.formats.big.hw1 import HomeworldBigFile
from naabal.formats.big.hw2 import Homeworld2BigFile
from naabal.formats.big.hwrm import HomeworldRemasteredBigFile, HomeworldClassicBigFile

def big_diff():
    parser = argparse.ArgumentParser(prog='big-diff',
        description='Compare two big files')
    parser.add_argument('left-file')
    parser.add_argument('right-file')
    args = parser.parse_args()

    with big_load(args.left_file) as left_big:
        with big_load(args.right_file) as right_big:
            if isinstance(left_big, HomeworldBigFile):
                for i, (left_m, right_m) in enumerate(zip(left_big['table_of_contents'], right_big['table_of_contents'])):
                    for struct_m in HomeworldBigFile.STRUCTURE[1][1].CHILD_TYPE.STRUCTURE:
                        key = struct_m['key']
                        left_v = left_m[key]
                        right_v = right_m[key]
                        if left_v != right_v:
                            sys.stdout.write('ToC mismatch on key [{0}]: {1} != {2}\n'.format(
                                key, repr(left_v), repr(right_v)))
            else:
                for i, (left_m, right_m) in enumerate(zip(left_big.get_members(), right_big.get_members())):
                    sys.stdout.write('Checking member #{0:06d}\n'.format(i))
                    for key in ['name', 'mtime', 'real_size', 'stored_size']:
                        left_v = getattr(left_m, key)
                        right_v = getattr(right_m, key)
                        if left_v != right_v:
                            sys.stdout.write('Member mismatch on key [{0}]: {1} != {2}\n'.format(
                                key, repr(left_v), repr(right_v)))

            left_size_total = sum(m.stored_size for m in left_big.get_members())
            right_size_total = sum(m.stored_size for m in right_big.get_members())
            if left_size_total != right_size_total:
                sys.stdout.write('Total data size does not match: {0:d} != {1:d} (+/- {2:d})\n'.format(
                    left_size_total, right_size_total, abs(right_size_total - left_size_total)))

CURRENT_YEAR = datetime.datetime.utcnow().year

def format_mtime(mtime):
    if mtime.year == CURRENT_YEAR:
        return mtime.strftime('%b %d %H:%M')
    else:
        return mtime.strftime('%b %d  %Y')

def big_ls():
    parser = argparse.ArgumentParser(prog='big-ls',
        description='List contents of a .big file')
    parser.add_argument('-l', '--long', action='store_true')
    parser.add_argument('filename')
    args = parser.parse_args()
    with big_load(args.filename) as bigfile:
        for member in bigfile:
            if args.long:
                sys.stdout.write('{0} {1:8d} +{2:8d} {3} {4}\n'.format(
                    'c' if member.is_compressed else 'N',
                    member.stored_size,
                    member.real_size - member.stored_size,
                    format_mtime(member.mtime),
                    member.name
                ))
            else:
                sys.stdout.write('{0}\n'.format(member.name))
    return 0

def big_extract():
    parser = argparse.ArgumentParser(prog='big-extract',
        description='Extract contents of a .big file to a directory')
    parser.add_argument('-i', '--include-matching')
    parser.add_argument('--no-decompress', action='store_false')
    parser.add_argument('filename')
    parser.add_argument('destination', default=os.getcwd(), nargs='?')
    args = parser.parse_args()

    with big_load(args.filename) as bigfile:
        if args.include_matching:
            member_list = [m for m in bigfile.get_members() if fnmatch.fnmatch(m.name, args.include_matching)]
        else:
            member_list = bigfile.get_members()
        for member in member_list:
            bigfile.extract(member, args.destination, args.no_decompress)
            sys.stdout.write('Extracted {size:8d} bytes: {name}\n'.format(
                size=member.real_size, name=member.name))
    return 0

def big_decrypt():
    parser = argparse.ArgumentParser(prog='big-decrypt',
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
    return 0

CREATE_FORMATS = {
    'hw1':      HomeworldBigFile,
    'hw1c':     HomeworldClassicBigFile,
    'hw2':      Homeworld2BigFile,
}

def big_create():
    parser = argparse.ArgumentParser(prog='big-create',
        description='Create a big file')
    parser.add_argument('-f', '--format', choices=CREATE_FORMATS, default='hw2')
    parser.add_argument('-x', '--exclude-matching')
    parser.add_argument('filename')
    parser.add_argument('source', default=os.getcwd(), nargs='?')
    args = parser.parse_args()

    with CREATE_FORMATS[args.format](args.filename, 'w') as bigfile:
        if args.exclude_matching:
            exclude = lambda fn: not fnmatch.fnmatch(fn, args.exclude_matching)
        else:
            exclude = None
        bigfile.add_all(args.source, exclude)
        bigfile.save()
    return 0


MAIN_IDX = {
    'ls':           big_ls,
    'diff':         big_diff,
    'extract':      big_extract,
    'decrypt':      big_decrypt,
    'create':       big_create,
}

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main = MAIN_IDX[sys.argv[1]]
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        main()
    else:
        sys.stdout.write('Usage: {0} <{1}> ...\n'.format(sys.argv[0], ', '.join(MAIN_IDX.keys())))
