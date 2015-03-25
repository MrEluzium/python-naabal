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
import datetime
import sys

from naabal.util.helpers import big_open


NOW_YEAR = datetime.datetime.utcnow().year

def format_mtime(mtime):
    if mtime.year == NOW_YEAR:
        return mtime.strftime('%b %d %H:%M')
    else:
        return mtime.strftime('%b %d  %Y')

def main():
    parser = argparse.ArgumentParser(prog='big-ls',
        description='List contents of a .big file')
    parser.add_argument('-l', '--long', action='store_true')
    parser.add_argument('filename')
    args = parser.parse_args()
    with big_open(args.filename) as bigfile:
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

if __name__ == '__main__':
    main()
