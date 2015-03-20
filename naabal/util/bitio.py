# @source http://rosettacode.org/wiki/Bitwise_IO#Python
# @license http://www.gnu.org/licenses/fdl-1.2.html

class BitIO(object):
    BITS_IN_BYTE    = 8

    def __init__(self, handle):
        self._data_buffer = handle
        self._reset()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.flush()

    def _reset(self):
        self._bit_buffer = 0x00
        self._bit_count = 0

    def flush(self):
        self._reset()

class BitWriter(BitIO):
    def write_bit(self, bit):
        if self._bit_count == self.BITS_IN_BYTE:
            self.flush()
        if bit > 0:
            self._bit_buffer |= (1 << (self.BITS_IN_BYTE - 1) - self._bit_count)
        self._bit_count += 1

    def write_bits(self, value, bit_count):
        while bit_count > 0:
            self.write_bit(value & (1 << (bit_count - 1)))
            bit_count -= 1

    def flush(self):
        if self._bit_count != 0:
            self._data_buffer.write(chr(self._bit_buffer))
        self._reset()

class BitReader(BitIO):
    def read_bit(self):
        if self._bit_count == 0:
            c = self._data_buffer.read(1)
            if len(c) != 0:
                self._bit_buffer = ord(c)
            self._bit_count = self.BITS_IN_BYTE
        bit_value = (self._bit_buffer & (1 << (self._bit_count - 1))) >> (self._bit_count - 1)
        self._bit_count -= 1
        return bit_value

    def read_bits(self, bit_count):
        bits_value = 0x00
        while bit_count > 0:
            bits_value = (bits_value << 1) | self.read_bit()
            bit_count -= 1
        return bits_value
