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

from setuptools import setup, find_packages

import naabal


with open('requirements.txt') as req_f:
    requirements = [l.strip() for l in req_f if l.strip()]

SETUP_ARGS = {
    # package metadata
    'name':             naabal.__title__,
    'description':      naabal.__description__,
    'long_description': naabal.__description__,
    'version':          naabal.__version__,
    'author':           naabal.__author__,
    'author_email':     naabal.__author_email__,
    'url':              naabal.__url__,

    # pypi metadata
    'license':          'MIT',
    'platforms':        'any',
    'install_requires': requirements,
    'classifiers':      [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Archiving',
    ],

    # setuptools info
    # 'package_dir':      {'': 'src'},
    'packages':         find_packages(),
    'entry_points':     {
        'console_scripts': [
            'big-ls             = naabal.scripts.big_ls:main',
            'big-extract        = naabal.scripts.big_extract:main',
            'big-decrypt        = naabal.scripts.big_decrypt:main',
        ],
    },
    'test_suite':       'tests',
}

if __name__ == '__main__':
    setup(**SETUP_ARGS)
