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


from naabal.formats.big.hw1 import HomeworldBigFile
from naabal.formats.big.hwcata import CataclysmBigFile
from naabal.formats.big.hw2 import Homeworld2BigFile
from naabal.formats.big.hwrm import \
    HomeworldClassicBigFile, Homeworld2ClassicBigFile, HomeworldRemasteredBigFile

FORMAT_IDX = {
    'hw1':      HomeworldBigFile,
    'hw1c':     HomeworldClassicBigFile,
    'hw2':      Homeworld2BigFile,
    'hw2c':     Homeworld2ClassicBigFile,
    'hwrm':     HomeworldRemasteredBigFile,
}

if __name__ == '__main__':
    import argparse
    import os
    import os.path
    import fnmatch

    parser = argparse.ArgumentParser(prog='big-extract.py',
        description='Extract contents of a .big file to a directory')
    parser.add_argument('-f', '--format', choices=FORMAT_IDX, required=True)
    parser.add_argument('-i', '--include-matching', nargs='+')
    parser.add_argument('filename')
    parser.add_argument('destination', default=os.getcwd(), nargs='?')
    args = parser.parse_args()

    if args.include_matching:
        should_extract = lambda fn: any(fnmatch.fnmatch(fn, pattern) for pattern in args.include_matching)
    else:
        should_extract = lambda fn: True

    with FORMAT_IDX[args.format](args.filename) as bigfile:
        for entry in bigfile:
            filename = bigfile.get_filename(entry)
            full_filename = os.path.join(args.destination, filename)
            if should_extract(filename):
                try:
                    os.makedirs(os.path.dirname(full_filename))
                except os.error:
                    # leaf dir already exists (probably)
                    pass
                with open(full_filename, 'w') as data_file:
                    data_file.write(bigfile.get_data(entry))
                print 'Extracted file: %s' % filename
