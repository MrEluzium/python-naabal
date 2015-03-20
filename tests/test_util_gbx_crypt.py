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

from naabal.util.gbx_crypt import GearboxCrypt
from naabal.util import unpack_key

TEST_GLOBAL_KEY1 = unpack_key("""
T10lnVvi4j4Mwktma0CjvH969QKh8zTQj5juzGltVCyjjmoBPwFYuc2Fmx3/FNG2xylCFeDz+4+D
ArZiqlIPEPIRpOfV//SAZV2DolPDq9yG4IP1QpQir42HHLJ16O66yl738iK7nxpKqwntzySVdE9m
NEZWmO4l9GXDznxGI3Tw798MaJ7rag7GkSBuzwoj/hdrc06czNQReRMhHNRAB/dOAaK43jlvoku8
nqQ+rJi6gKj63Jis8DY8WmOEShDU1iVubWNVTzxXnKkpfDoLCdIw28OCoD0pNu20VMn11kis81uf
bXuis6pbcPEowMXzgiv4cRuxm5Sd730bmnFHlcuByeqHUDbyHZRGKdHdtET1tmRg7qWxz/j/EMZV
CmAYK0T1RaT747/gC6588B985pg7Z6tOToD/jGnQ8fOXxijz+XohPZjbVnk7b8yH9raxpWb8Z+DJ
Vh6BjQyfpZczkzxpSHCVS/pU7BYGa+T4PhyuKjQzNF+hrcbdePXRrQrrld42EIMrLGGYl3JL3dhw
9WDf+fHYlvN5cP2ETkCQjJKCBvps5/qvUTjH5u1S7DvgShFsXt/V3g+x429rq+s8hSeP/Rk/5oJr
4jkvTUsC+tCBkHEXT8r1sv3G4/uca8XorxCgVuz/RbTtNFBAgR6z+uNIHVNyUtbRcd39jCvji/Yp
pTFz28fqpC206LEksHBpOUYp8bv3BOOH5AAmBa0pHfSHKj/A/9lSw26EbAN2QdZP7gKfCf6yG5G9
ARlLTW5BY/hw1Fsp+s7ENyHZG9arr+BMbsy0nEdQfky/dfin4qARqvZk25C6CVMKzPhNmjo9UzHB
seUTUcJ3I0s6lt4aXRrU21k23EXa45ObmCOT0oiq/sdNMf0EGYrRMiMv65yhnVJ8CVY+/D8ejEl9
2Q4ObreR4CbmXsN9VNwuCO/n9qZG5135NMeqOA4y5kZveRPckQRHJRX8DlPYVqPRxNJ4wa/QLQgs
VcbBFV631pXyKef8kxTMCR6Wc2AY9z3vBOfh7DqlizWknZocFZmjVOP65k2QrGexmWL3Bl8l1m6H
TMUwROb9UepSrkBlQojV/OAeRXskU8TJCwrPRr4py6S/MMilsEFU2lmARfb68zX3BjDxQf/tV51o
iVrWmmNeG2q+7h05vSsKumBMYJC6Oal0U/pjUxEb6qZa0c6szE8MpiWeBSL6d9ZTpAYmnQvKg2yc
dsdE07JhLk+ywRVt4y5OveKU6lI01xjJoWp2Ei7OZudr5gOr0ryXZfg0hdS0JCnZdtGmWoyvVHFf
QMqyPUMs03FkPIsMpEWIdn5A5vGcLp595GoYc/SPBs9AYge30O2gLlxSUBpvRRzWpr6sCrQPCQ==
""")

TEST_LOCAL_KEY1 = unpack_key("""
nuMUCCs5Dhx39whw13B0LQKqXi3oTao73WOK2DYLYMh6+cqtphvMmiKYpiI2UkHdS7eE0H2xuwCI
lSUuVe9lCaLFu8+8QMN2JtRS9Pz8qkU9nYp5QfsQrKMOETZWM0UNeU5FRkURne1DhiB8qJJMQWuQ
gd67Nh6I9gchgmqYWxIa+b1qsQpVfJ8CA6b7S1sT/kBoyzuCtaB29x9YAlvIBpL7x86WaxsDSUo8
aOMaDU5cMi1qZ2Bx6Xh5mfj9bsDZ2XJ1W05dAvvLO/nnrEtgZHFz+amXcBv1okPvrvXLT8sMtj3Y
myGAFuprxtvIE4Uk9soeY2cJOKN36OW4RFQODA==
""")

TEST_COMBINED_KEY1 = unpack_key("""
p7Hl7cLCXrPsU/0+gQtbJmCZuyqmXvlcm+y15X738wp54gt+cW02XL3GCRqs+79dtQf7e3KoxEgk
vbOKYrXt57Sk5dghEStUgW+un6ACypr8cpc5Ea1cfRpDBFjpG4dhBbvxHSnkhgJ/Y6GV68ZMkmqJ
UFD5+fS0xMhrfidOK9xkS8VaMXl4/EB36Bg4xNVmaIOQmucfaZXlOKTWiqtx4MG68Ncz6J7oFMLg
9gZMd04/ZkX266MCSAyGp0M0dqdLjzgAX1Io2PAyVus6Rf6R2F+dU+IYC1m05f6SRGE4Qtf/vJMk
K5zL/29owup1NrwzMIIhOvGSGw517HCAjghthA==
""")

TEST_DATA = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque quis
malesuada leo. Mauris id nunc faucibus, rhoncus lacus a, convallis quam. Morbi
vel semper leo. Etiam elementum, massa at feugiat cursus, ante massa eleifend
mi, eu commodo lacus diam quis elit. Vestibulum eu quam lacinia, dapibus nibh
sit amet, tempor nisl. Suspendisse venenatis malesuada orci, id pellentesque
purus aliquam nec. Fusce vel risus vitae neque convallis tempus. Aliquam vel
mollis elit, eget mattis massa.  Nunc pulvinar augue enim, eget efficitur augue
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

TEST_DATA_ENCRYPTED = """
pb6NeKteC72HInDi42QRSRKHuD/OwmgRyoh3O+V4e2nsgWnnAwg8xKSeYFa9eKQMuWAl6vrBsOb8
k7LiCrCBjbHPjJ1ED0Yh6ARczsFqm9l5780oD78J8hTdSQmMV+ISG65zA0WR6GGhA8DgeKMW4wmj
0CJvdnqvsau17joVSpe8FmfGMvb2eiH1hFE7XJwP+eqehmZQCc2E0tKP4nUChay2dZvthMeHGl5l
fmMV9tImBiB3estyLWGmeSot/cwWkSl0wRQ9nXc3C4nmHnfhmxbW2T5JYxuxO2/PLxIp3o5tqdZC
OtKZC/4BajbwP2QwP+tMNXPdBV7sdwXzklz83cZvjIinscKygBZ38J9LCk0U0KdLxhd0xMqJa4z3
anoW839Y6/38K9BjnlhWvWe2Fmtnbuf2Yq8hUGOu4wO/PznAwYiYTmH1GugEvo+AUavZdPPXK1jG
F+gGM2EWfFPaE2S4L1A4iN9x9v7DzDWpJtH/o9AZayd8saik+vBNF0iVERpFFkT5/Xfg6oRRObGM
B7jr1clHAd3gjivBSuy6+0Cxr4OeQDjYgWCfhSpoGfonJroeeYPTXyRg48zdQO/GJeY7LsHvRJGB
QwuC5jFn2zIO0hmKUWjHsYdr4ui/LSWOdWTaPUnYnnSxBZ+J/ity7fDMVDRyjlVn94r57tNqs93O
tpB4XqMQtoHZIyfmWhn6Bc2rP70LexnXNKyQ6X5yAPuDYvL+BeoFcVpEVcZnqsOsGXb678VcJkG0
wtvMa2OLrcGOjU1j9R/oBXLCzWOqhnH3iTRevxDsWekcCYNO6hRguS9IRYXnHuIRi3V4qSLh+9ok
FXt8fmyxqgPjB9IqmLwjqhTv9/ppNPKNVeipkA4N8J6GaUn43oA0yJ/pdQOFrLZ/m+2I1H1gp5V3
Gin7ICLG22uJZ2EnYvC6KTjzzNXWQCARHUuddUAPNSswMI97FtYdg1ZZEL+OZ44iAD0hkmO54PxI
xaVq9gZegAA9uDz8nlA7eOEFZvSC8+nWbQHwebOQfEijDrKBEnE29GLFUAnbpjuIwloJyTS4fPpy
emv6Pl7wr/8zBqisZgbCdK/Dt1po7vzBneb8hsLo/618jcHOO45EWz4fn/230IweqdVo79UsYl0N
8QYiaBGLBeINJ2VzREeF3HP0vcjMeK8g1wmXESJqfDpsiZkK9EIl9ZH9IaAZROjsZeD9ilE7sJQL
DeKQ1X1KBpc7PsGWlrf4gqS0dJ46Ith9WKeUKl0j9yUm/S9vidJw2GLpx+vszc4n0ippFSNKSHw9
DIQ4L2viSA7MzYxXY8fAgG7aMRLoMYxmsNJOPtemdva4o3zxM6c2RPNR9Bm8Rl+reQSg13Cz8s67
i4iynxayQM12J+xlCkzAy7RCyRQnBchAa33uanta8JIV5wH0PtJjfmZUuWhhE7Nad+oCyp3YRrjA
6g1reI1WyISKRGFEzOj+wsbSYp/LeLqJNV7BxOZVK28NelneE3C3L1FMiOZfoRPU14WvKM8K3N7Q
WmxwbK2t/vX5GDqWCRqpGkT0qHcl9kYIFrGZ/aLw0c2CVQvUjvR8ndfF+IWtZnaOP4XHhmCzjSpw
GfEbJA8nazXTYyZZ6LoxNf2F1d89bgTOPaAwPhJ2OCB24YnBzxKNFBUasX8i1x0CPSqSdE7OUTzZ
miH++bOI9D1kQDXi/zNw41db/kKww+dq9N7Cw5CFXp/Cw3kZbDafYwo9wMi3Oc/CdxbKiLSQ7ylz
X/WHV/cCweryuKZjR15roga0ZW7494Y=
""".strip().decode('base64')

class TestUtilGbxCrypt(unittest.TestCase):
    def setUp(self):
        self.crypto = GearboxCrypt(len(TEST_DATA), TEST_LOCAL_KEY1, TEST_GLOBAL_KEY1)

    def tearDown(self):
        self.crypto = None

    def test_combined_key(self):
        self.assertEqual(TEST_COMBINED_KEY1, self.crypto._encryption_key)

    def test_decrypt(self):
        self.assertEqual(TEST_DATA, self.crypto.decrypt(TEST_DATA_ENCRYPTED))

    def test_partial_decrypt(self):
        partial_start = len(TEST_DATA) / 2
        partial_length = 25
        partial_end = partial_start + partial_length

        self.assertEqual(TEST_DATA[partial_start:partial_end],
            self.crypto.decrypt(TEST_DATA_ENCRYPTED[partial_start:partial_end],
                partial_start))

    def test_encrypt(self):
        self.assertEqual(TEST_DATA_ENCRYPTED, self.crypto.encrypt(TEST_DATA))

    def test_partial_encrypt(self):
        partial_start = len(TEST_DATA) / 2
        partial_length = 25
        partial_end = partial_start + partial_length

        self.assertEqual(TEST_DATA_ENCRYPTED[partial_start:partial_end],
            self.crypto.encrypt(TEST_DATA[partial_start:partial_end],
                partial_start))

if __name__ == '__main__':
    unittest.main()
