# @source http://rosettacode.org/wiki/Bitwise_IO#Python
# @license http://www.gnu.org/licenses/fdl-1.2.html

class BitIO(object):
    BITS_IN_BYTE    = 8
    DEFAULT_MASK    = 1 << (BITS_IN_BYTE - 1) # 0x80

    def __init__(self, handle):
        self._data_buffer = handle
        self._bit_buffer = 0x00
        self._bit_mask = self.DEFAULT_MASK
        self._bit_idx = 0

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        pass

class BitWriter(BitIO):
    def __exit__(self, type, value, tb):
        self.flush()

    def write_bit(self, bit):
        if bit:
            self._bit_buffer |= self._bit_mask
        self._bit_mask = self._bit_mask >> 1
        if self._bit_mask == 0:
            self._flush_bit_buffer()
            self._reset_state()

    def write_bits(self, value, bit_count):
        mask = 1 << (bit_count - 1)

        while mask != 0:
            if mask & value:
                self._bit_buffer |= self._bit_mask
            self._bit_mask = self._bit_mask >> 1
            if self._bit_mask == 0:
                self._flush_bit_buffer()
                self._reset_state()
            mask = mask >> 1

    def flush(self):
        if self._bit_mask != self.DEFAULT_MASK:
            self._flush_bit_buffer()
            self._reset_state()
        return self._bit_idx

    def _flush_bit_buffer(self):
        self._data_buffer.write(chr(self._bit_buffer))
        self._bit_idx += 1

    def _reset_state(self):
        self._bit_buffer = 0x00
        self._bit_mask   = self.DEFAULT_MASK

class BitReader(BitIO):
    def read_bit(self):
        if self._bit_mask == self.DEFAULT_MASK:
            self._load_bit_buffer()

        value = self._bit_buffer & self._bit_mask
        self._bit_mask = self._bit_mask >> 1
        if self._bit_mask == 0:
            self._bit_mask = self.DEFAULT_MASK

        return 1 if value else 0

    def read_bits(self, bit_count):
        mask = 1 << (bit_count - 1)
        bits_value = 0x00

        while mask != 0:
            if self._bit_mask == self.DEFAULT_MASK:
                self._load_bit_buffer()

            if self._bit_buffer & self._bit_mask:
                bits_value |= mask
            mask = mask >> 1
            self._bit_mask = self._bit_mask >> 1
            if self._bit_mask == 0:
                self._bit_mask = self.DEFAULT_MASK

        return bits_value

    def _load_bit_buffer(self):
        c = self._data_buffer.read(1)
        self._bit_buffer = ord(c)
        self._bit_idx += 1
