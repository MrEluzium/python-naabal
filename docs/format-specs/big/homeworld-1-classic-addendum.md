# Homeworld 1 Classic BIG Addendum

The BIG format used in Homeworld 1 Classic from Gearbox is slightly different
from the original format. The changes only concern the ToC entry struct.

## Table of Contents

The contents of a ToC entry struct are:

* `unsigned long` (4 bytes) name crc1
* `unsigned long` (4 bytes) name crc2
* `unsigned long` (4 bytes) name length
* `unsigned char` (1 byte) unused padding1
* `unsigned long` (4 bytes) stored size
* `unsigned long` (4 bytes) real size
* `unsigned long` (4 bytes) offset
* `unsigned long` (4 bytes) timestamp
* `unsigned long` (4 bytes) unused padding2
* `unsigned long` (4 bytes) compression flag

The `unused padding1` is a single byte with the value `0xA7`.

The `unused padding2` is a 4 bytes with the value of `{ 0x00, 0x00, 0x00, 0x00 }`.

Note that the original `unused padding` after the `compression flag` is not found
in the new format.
