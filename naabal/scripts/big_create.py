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
import fnmatch
import os

from naabal.formats.big.hw1 import HomeworldBigFile
from naabal.formats.big.hw2 import Homeworld2BigFile
from naabal.formats.big.hwrm import HomeworldClassicBigFile


FORMATS = {
    'hw1':      HomeworldBigFile,
    'hw1c':     HomeworldClassicBigFile,
    'hw2':      Homeworld2BigFile,
}

def main():
    parser = argparse.ArgumentParser(prog='big-create',
        description='Create a big file')
    parser.add_argument('-f', '--format', choices=FORMATS, default='hw2')
    parser.add_argument('-x', '--exclude-matching')
    parser.add_argument('filename')
    parser.add_argument('source', default=os.getcwd(), nargs='?')
    args = parser.parse_args()

    with FORMATS[args.format](args.filename, 'w') as bigfile:
        if args.exclude_matching:
            exclude = lambda fn: not fnmatch.fnmatch(fn, args.exclude_matching)
        else:
            exclude = None
        bigfile.add_all(args.source, exclude)
        bigfile.save()
    return 0

if __name__ == '__main__':
    main()
