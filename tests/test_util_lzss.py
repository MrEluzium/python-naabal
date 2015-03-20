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
""".strip()

TEST_DATA1_COMPRESSED = """
plvuVltsgtNwud1tsgslvtlvuUgudpukgsNtst0lkgsdvt1zstjullul1uUgsNktNwtNzsdpt1nk
FltlpukukFQststllt10stzuN1ssguN1tNzhVtsNsstzuthslhkFsstvl0gpthutytNzkFpskgt1
1t1jkFmsN1sdpsV1ucskFytFvt1jutzkFssNjutzkFhlkgsdvt12sNstlpucguN1sNtl0gptvuVi
tMKu1ltkgudlttwstykFsstvl0got0tNhtsgstssttstuul1tsskFtsNzudhkFhukgs1lutntNhu
kgsd1uVzutzlkgsNuullkFtsNzudhkFltlltNmstuskKttplkgst1kFjt9tttvslvkFssNjutzkF
ktNhtsguN1tNzkFltlpukukFWstzulpsV1tl1tsgst1kFxuthtsgtlhsdpt1psMskFksNwtNiutz
kFutNitEKudpukgsNtst0lkgullttwt9ykFutNztkukFTutzuFlt1ktNzudlkF2stustusN0tNzk
FtsNsstzuthslhkFvuVjtMskFpskguFltlsstuulludxutlhVwutyutzkFhtlpuN1sNtkFustjl0
go11udjssgu1ltkguVpud1ucgu1pulhssgt1luN1ssgsdvt12sNstlpucgullttwutzl0goNstNx
uthtsgu1ltkKttvtlstNzkFltlpukskFls9lukgtthul0tNzkFtsNzudhl0KhVOutuscguF1tl2t
NusNykFhutnutlkFlt1ptsskFls9lukgstms1psdpul1uUgsN1s91ssKullttwt9ykFhl0gptvuV
itMgsMguN1sNtkFustxutll0gqFysNludlt10kFztN0kFhttlukgttpkFtt9stlpucskFhtlpuN1
st0kFlt1ptsgsN0lkKsdvt1zstjullul1uUgutyt1hl0gqt0kFut9ukFwuVlulputtkFtst0utzl
0gqFosNzststl1ucgullttwt9ykFwuVlulputtkF1uVusMskFhukKsdvt12sNstlpucgst4kFwt9
zutluVlkFlusukFTutzuFlt1ktNzudlkFmsN1sdpsV1ucgudhuFpstukFqutzulvlkguN1tNzkF0
tNusdpsl1t10kFkutphVltllttlt10uttkF2tN0sNll0gqdlskgtthvFptt1ucgtNukFstNistyt
8gt1vt0gtlhsdpt1psMukFDutysNitN0utykFmststNzkFsstvlkgudvslhtllucKtNukFltlpuk
gtNulkgslhuFpsV1ucgtNhsd1tlpucgsNysd1l0gpthutytNzkFtsNsstzuthslhkF0uVpud0tNx
utlkFvslpt8skF2stskFitNistusl1tsKu1ltlpukgsdvt1zstjullul1uUgt1vt0ukFDutysNit
N0utykFst9it9yulpucgttpkFut9ukF0ststl1ucgudjstsstytNzuN1ssgstms1psdpul1uUuhV
OsNtkFlukgst4kF2utsuF1ulhulllkgudlttwstykFkt9st9ykFhscskFitlht1ktN0kFluVhuku
kFEt9ustjkFwtFhuVlulysMgtV1ud0t8gst0hVstNistyt8gtNtuFluVktNlukskFut9ukFjt9uu
dlsd0st0utykFuutstlhkF2utsuF1ulhulll0gqdlskguN1tNzkFmstyttlt10uttkFzsttl0gp1
1t1jhVzsNntN0ulpucskFzsNwtNlt0gs1luVtstuul1tsgu1ltFpsd1tlhkF2stustusN0tNzlkg
t11t1jkFlvEguFosNyst0uVhkFsstvlkgudlskgtNhsd1tlpucKsN1s91ssgtthutytNzkFzstkk
FtsN1uVpucukFDutysNitN0utykFhkF2ststN0kFustjkFhuVjusguFyst0tN1tsgs1pt1psV1uc
ukFOutstlhhVmsNjtNstNztIAAA=
""".strip().decode('base64')

class TestUtilLzss(unittest.TestCase):
    def test_decompression(self):
        self.assertEqual(TEST_DATA1_DECOMPRESSED, decompress(TEST_DATA1_COMPRESSED))

    def test_compression(self):
        self.assertEqual(TEST_DATA1_COMPRESSED, compress(TEST_DATA1_DECOMPRESSED))

if __name__ == '__main__':
    unittest.main()
