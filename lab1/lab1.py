
"""
Python version 3.6.2
This program allow to encode/decode files from/to base64
usage:
Encode with -e, Decode -d
python lab1.py inputFile -e outputFile
Implementation based on RFC 2045
"""

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
           'abcdefghijklmnopqrstuvwxyz' \
           '0123456789+/'
"""
Steps
[x] encode string (encoding mechanism )
[ ] decode string (decoding mechanism )
[ ] file handling
[ ] adjust program to options -d and -e
"""

def base64_encode(filename):
    with open(filename, "rb") as file:
        # read exactly 3 bytes - 24 bits
        final_base64_string = ""

        while True:
            slice_of_file = file.read(3)
            if slice_of_file == b'':
                break

            # count how many bits you have
            read_bits = 8 * len(slice_of_file)
            # how many '=' you must add
            padding = 3 - len(slice_of_file)

            # align to 6 bits chunks
            zeros_to_add = (24 - read_bits) % 6
            aligned_chunk = int.from_bytes(slice_of_file, byteorder='big')
            aligned_chunk <<= zeros_to_add

            b64_chunk = ""

            while aligned_chunk != 0:
                # get 6 bits
                b64_sign = aligned_chunk & 0b111111
                b64_chunk += ALPHABET[b64_sign]

                # remove first 6 bits
                aligned_chunk >>= 6

            # reverse string order
            b64_chunk = b64_chunk[::-1]
            # padding
            b64_chunk = b64_chunk + (padding * '=')
            # add b64_chunk to final string
            final_base64_string += b64_chunk

    return final_base64_string


if __name__ == "__main__":


