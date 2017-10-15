from math import ceil
import argparse

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
[x] decode string (decoding mechanism )
[x] file handling
[x] adjust program to options -d and -e
"""


def base64_encode(filename):

    final_base64_string = ''

    with open(filename, 'rb') as file:
        while True:
            # read exactly 3 bytes - 24 bits
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

            b64_chunk = ''

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


def base64_decode(filename):
    final_bytes_string = b''

    with open(filename, 'r') as file:
        input_string = file.read().replace('=', '')
        bytes_value = 0
        curr_bits = 6 * len(input_string)
        output_bits = curr_bits - (curr_bits % 8 )

        for char in input_string:
            bytes_value <<= 6
            number_value_of_char = ALPHABET.index(char)
            bytes_value ^= number_value_of_char

        bytes_value >>= abs(output_bits - curr_bits)
        final_bytes_string = bytes_value.to_bytes(output_bits // 8, byteorder='big')

    return final_bytes_string


def saveStringToFile(filename, _string):
    with open(filename, "w") as file:
        file.write(_string)


def saveBytesToFile(filename, _bytes):
    with open(filename, "wb") as file:
        file.write(_bytes)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('input_filename', metavar='InputFileName', type=str,
                        help='name of input file to process')

    parser.add_argument('output_filename', metavar='OutputFileName', type=str,
                        help='name of output file to ')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e', '--encode', action='store_true', help='encode input file to base64')
    group.add_argument('-d', '--decode', action='store_true', help='decode input file from base64 encoding')

    args = parser.parse_args()
    _dict_vars = vars(args)

    if _dict_vars['encode']:
        result = base64_encode(_dict_vars['input_filename'])
        saveStringToFile(_dict_vars['output_filename'], result)
    elif _dict_vars['decode']:
        _bytes = base64_decode(_dict_vars['input_filename'])
        saveBytesToFile(_dict_vars['output_filename'], _bytes)


