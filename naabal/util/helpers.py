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

import logging

from naabal.formats.big.hw1 import HomeworldBigFile
from naabal.formats.big.hw2 import Homeworld2BigFile
from naabal.formats.big.hwrm import HomeworldClassicBigFile, HomeworldRemasteredBigFile

logger = logging.getLogger('naabal.util.helpers')

BIG_FORMATS     = [
    HomeworldRemasteredBigFile,
    Homeworld2BigFile,
    HomeworldClassicBigFile,
    HomeworldBigFile,
]

def big_open(filename, mode='rb'):
    logger.info('Attempting to determine format for big file: %s', filename)
    for big_fmt in BIG_FORMATS:
        logger.debug('Trying format: %s', big_fmt)
        bigfile = big_fmt(filename, mode)
        try:
            bigfile.load()
        except Exception as err:
            logger.debug('Loading failed for format: %s', big_fmt)
            logger.exception(err)
        else:
            logger.info('Determined format as: %r', big_fmt)
            return bigfile
    else:
        raise ValueError('Unable to determine appropriate .big format')
