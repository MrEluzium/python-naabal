# Homeworld 1 BIG Format Spec

This specification describes the format of the .BIG archive files used in the
1999 title *Homeworld* by Relic Entertainment inc. The BIG format is a container
for other files, and is conceptually similar to any other archive format such
as TAR or ZIP. The main difference is that it is not easily practical to extend an
archive after first creating it.

## Specification

The overall format is:

    * Header
    * Table of Contents (ToC)
    * File blobs

### Header

The header is a fixed size struct of 15 bytes at the beginning of the file
(offset 0x00) and occurs only once.

The contents of a header struct are:

    * `char[3]` (3 bytes) file signature
    * `char[4]` (4 bytes) format version
    * `int` (4 bytes) file count
    * `int` (4 bytes) flags

The `file signature` should always be "RBF". The only known value for the
`format version` is "1.23". Additionally, the Homeworld source code shows that
the version is hard-coded as "1.23" so files with a different version would not
be recogonized as valid.

The `file count` is the number of Table of Contents entries to follow in the
Table of Contents section.

The `flags` was intended to be used to note whether the ToC list
was sorted or not, but in practice it is always `0x00000001` as the ToC is always
sorted. See the ToC Sorting section.

### Table of Contents

The ToC is a series of fixed size structs of 32 bytes immediately following the
header (offset 0x0F) and occurs only once. The ToC entries themselves describe
a file contained in the archive.

The contents of a ToC entry struct are:

    * `unsigned long` (4 bytes) name crc1
    * `unsigned long` (4 bytes) name crc2
    * `unsigned long` (4 bytes) name length
    * `unsigned long` (4 bytes) stored size
    * `unsigned long` (4 bytes) real size
    * `unsigned long` (4 bytes) offset
    * `unsigned long` (4 bytes) timestamp
    * `char` (1 byte) compression flag
    * `unsigned char[3]` (3 bytes) unused padding

The `name crc` fields are the standard CRC32 checksums of the the filename
(converted to lower-case) split in half. Note that there is actually a bug in the
method used to calculate them, such that for filenames with odd lengths the last
character is not included in the second CRC32 value. A psuedo-code implementation
looks something like this:

    function relic_crc_values(str filename) {
        filename = str_to_lower(filename)
        half_len = len(filename) / 2
        crc1 = crc32(filename[:half_len])
        crc2 = crc32(filename[half_len:half_len * 2])
        return crc1, crc2
    }

The `name length` is the length of the filename. When the filename is written out
there will be a null byte included at the end (null terminated string) but that
byte is not included in this field. It is worth noting that this field is
declared as a `unsigned short` in the original source code.

The `stored size` is the number of bytes of file data actually written to the
archive, after compression if the file is to be compressed.

The `real size` is the original size of the file data before compression. For
uncompressed files it should match the `stored size` field.

The `offset` is the absolute offset of the file blob.

The `timestamp` is a standard POSIX UTC timestamp; the number of seconds since the
UNIX epoch.

The `compression flag` is a simple flag to indicate whether the file data is
compressed, and thus should be decompressed when extracting. It is somewhat
redundant since you can determine the same thing by comparing the stored size and
real size. See the Compression section.

The `unused padding` is compiler-added padding that is not present in the original
source code. In practice it seems to always have the value of `{ 0xC9, 0xCA, 0xCB }`
but it is likely that any value would work just as well.

### File Blobs

The file blobs consist of a null-terminated string for the filename, followed by
the compressed (or not) file contents.

The filename has a couple considerations to be aware of:

    * The filename should have Windows-style path separators, i.e. backslashes (\)
    * The filename is stored in the original case. This is important as the CRC32
    values of the filename are calculated based on the lower-case version of the
    filename, so two filenames that differ only by case would have the same CRC32
    values and should be avoided.
    * The filename is also not stored in plaintext, it has a simple XOR encoding
    method run on it first. See the XOR Encryption section.

## Additional Notes

### XOR Encryption

This is some code for both the encryption and decryption of a filename in-place:

    void xor_run(char* buffer, ulong_t buffer_size)
    {
        char last_char;
        ulong_t i;
        last_char = (char)0xD5;

        for (i = 0; i < buffer_size; i++)
        {
            last_char ^= buffer[i];
            buffer[i] = last_char;
        }
    }

### Compression

The compression scheme used for file data is [LZSS](http://en.wikipedia.org/wiki/Lempel%E2%80%93Ziv%E2%80%93Storer%E2%80%93Szymanski)
with the following notes:

    * 1 bit signals passthrough character
    * 0 bit signals back reference
    * 12 bit index field
    * 4 bit length field

### ToC Sorting

The ToC entries should be sorted according to
the name crc fields, psuedo-code for getting the sort key value would be:

    function relic_toc_sort_key(struct toc_entry) {
        return (toc_entry.name_crc1 << 32) | toc_entry.name_crc2
    }
