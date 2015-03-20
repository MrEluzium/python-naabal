#!/usr/bin/env python
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

import unittest

from naabal.util.lzss import decompress, compress


TEST_DATA1_DECOMPRESSED = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque quis
malesuada leo. Mauris id nunc faucibus, rhoncus lacus a, convallis quam. Morbi
vel semper leo. Etiam elementum, massa at feugiat cursus, ante massa eleifend
mi, eu commodo lacus diam quis elit. Vestibulum eu quam lacinia, dapibus nibh
sit amet, tempor nisl. Suspendisse venenatis malesuada orci, id pellentesque
purus aliquam nec. Fusce vel risus vitae neque convallis tempus. Aliquam vel
mollis elit, eget mattis massa.

Nunc pulvinar augue enim, eget efficitur augue
tempor a. Morbi a quam neque. Praesent sit amet mi mollis, aliquet enim at,
consectetur urna. Ut non pretium metus. Phasellus tempor pretium urna, at
convallis ex posuere eu. Suspendisse faucibus sapien justo, quis tincidunt dui
elementum vitae. Sed maximus in libero non lacinia. Curabitur felis leo, sodales
in elit in, dapibus iaculis arcu. Mauris malesuada tristique odio, vel bibendum
velit consectetur non. Curabitur lobortis mi non tellus scelerisque efficitur.
Nam et ex vulputate, semper dolor ac, blandit erat. Donec pharetra justo et
libero imperdiet, non consectetur nulla vulputate. Sed quis fermentum sem. Nunc
sagittis, sapien fermentum vehicula venenatis, nunc ex pharetra leo, sed iaculis
augue mauris sed mauris. Curabitur a velit nec arcu pretium finibus. Nulla
facilisi.

Suspendisse in eros nulla. Mauris varius laoreet metus, nec volutpat lacus
euismod ut. Nullam ac imperdiet lorem. Cras et felis a tellus interdum interdum.
Aliquam id justo vel turpis ultrices feugiat id et diam. Maecenas consectetur ex
at tempor interdum. Nam scelerisque feugiat rhoncus. Nulla in tincidunt est.
""".strip()

TEST_DATA1_COMPRESSED = """
plvuVltsgtNwud1AChZLfbAAQSC52m6SCw22y3SWSCx2+3XOy2O6AGQuoBELDZAA4Wm52O026zyC
y2wAoEukFQAaBbLLbgEYXO43WyyACGAC0IVbbCA9AASACkLDIAJwW8BwFNsICYAJIABgskgt11t1
jkFmAuAAvCxXW5gGwuVoAPBYwOAAVQsIHgrCAbO7ATQAagB6ACGABcALIgEAsVphV2AaAASAAIFw
soCcAKx0W6WkEiADMQUAAPhAFACDACYFzuYFQLCAVCzWW62cFaAMMAPwXIASAHEbCA/EF2oLEbSD
FC3WQCWFpBdADGAA4NtttvAGgB7UBUAK4QI5AM1qwE8AVgAbwtgAoQdogjyA9kAwAFaAOsAKYALA
A3iBkAIkFohQBOAa4AoQAICEyC52wIYFTA4ACiAHMAUkAEASAE2FuBygDCAEYIEyASwAbQB1gBiE
KiADyIVcAZwAfyBFgEcMK4FjBUhRgp4WMKwQJ0ALwhLxuwQoLCDYAK4AEMgQsBQSDMACpCghi1DO
iDoAAcAIsgGhA6xs4BkAbI3QLAgNwZdCoVTgMxBhAtgacArwAJxBjgGwEL2FpBciHeOy2azWkJGA
CUxAJQoKCoe4ASiAgQCNoGtMBwNyDVACfAGsABJw8QCLwDooDTEOMQg4hA4gwRlkKAO0DOAP4AUw
KqJPC3AdgD7AADAPMARYQnghwSqFoBegA7ENIIUFRQzCeSBpjdBNhAiFst4FChbwtAAowECDdQpm
AamBPAErEK6EgtQU8LpbwXQBAzCwAH0ALoAfMBB4C/QBMgCxcNMgs4bKBjAPGF4EEAD7EP2AFUAm
YCyAB7AKCIJCocMKGJ2CwiLgE6kDkAV6QKYQn4XMHoAE0oUMjEOwQyIQlEDNgBmgHUIP6A20ALLh
ZIug3wRfABryGoBaRpghnSGfAMoAKmAAoATRDXBE20KCEZxQA8LEACAPMYlIBQRCIQFNGGZEamA4
sRyBCEXD3hTgVxCYhFhBdhtwBwAGJAPYAaaIKBABqBIgFZBYgfABUxH9iJAABuNEA7AGTAWGApYB
U4jPAF1oP5GFDJlGPACiEcqAT0hlpDrbIAgEhAf/AxVBeZg5AuQwlSBYiKQD5EE2CwgyADykQJEX
MhH6A5oWgfcA24CNAhW2IpCBmIWCRDFhpSDGBG1rChACDGwG9mTXInSgziiWhDWyIWENzIUK4+0A
mQikSJGgRmGFC3AF9gJXG0h7xFoUNXIZUATASMpDd3DbAGhADyYAIRJxCjyIpCQtG7ADgI3BcAYQ
gfDGCgL0EHmIngCE4lKDEziQuAiS48cQAYk+hISgK/EGGQ28x67FIADegRNAo4JcJimwBxWAxCQ5
QE2Q/EQFgirQtg4oR8AEfCBjoXdEQcIP4gLJBkwCuiNxAdbRMYCcQCRgEQqXLcpOAcoR79F+mA6K
WOUZEQviAh4y4AAA
""".strip().decode('base64')

class TestUtilLzss(unittest.TestCase):
    @unittest.skip('redundant')
    def test_roundtrip(self):
        comp_data = compress(TEST_DATA1_DECOMPRESSED)
        decomp_data = decompress(comp_data)
        self.assertEqual(TEST_DATA1_DECOMPRESSED, decomp_data)

    def test_decompression(self):
        self.assertEqual(TEST_DATA1_DECOMPRESSED, decompress(TEST_DATA1_COMPRESSED))

    def test_compression(self):
        self.assertEqual(TEST_DATA1_COMPRESSED, compress(TEST_DATA1_DECOMPRESSED))

if __name__ == '__main__':
    unittest.main()
