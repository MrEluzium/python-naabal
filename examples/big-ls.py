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

    parser = argparse.ArgumentParser(prog='big-ls.py',
        description='List contents of a .big file')
    parser.add_argument('-f', '--format', choices=FORMAT_IDX, required=True)
    parser.add_argument('filename')
    args = parser.parse_args()
    with FORMAT_IDX[args.format](args.filename) as bigfile:
        for entry in bigfile:
            print '{name_crc_start:0>8X}:{name_crc_end:0>8X} {state} {data_stored_size:>8} {data_real_size:>8} {timestamp} {filename}'.format(
                filename=bigfile.get_filename(entry), state='c' if entry['data_compressed_flag'] else 'F',
                name_crc_start=entry['name_crc_start'], name_crc_end=entry['name_crc_end'],
                data_real_size=entry['data_real_size'], data_stored_size=entry['data_stored_size'],
                timestamp=str(entry['timestamp']))
