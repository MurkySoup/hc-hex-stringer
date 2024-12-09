#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Hashcat Hex Password Format Converter, Version 0.7.3-Beta (Do Not Distribute)
By Rick Pelletier (galiagante@gmail.com), 25 September 2022
Last update: 09 December 2024

Example usage:

# ./hc-hex-stringer.py --string 'marquee:' --encode
$HEX[6d6172717565653a]

# ./hc-hex-stringer.py --string '$HEX[262333393a313539373533]' --decode
&#39:159753

In the event of an encoding or decoding error (for example, chardet could not
identify the correct character set to perform a conversion), nothing will be
displayed, but an exit code of '1' will be returned to the O/S. Successful
en/decoding will return the converted string and an exit code of '0'.
"""


import sys
import argparse
import chardet


def is_hexstring(string:str):
    if len(string) % 2 != 0:
        return False

    try:
        for s in string:
            int(s, 16)

        return True
    except:
        return False


def hc_hex_to_str(hex_string:str):
    if hex_string.startswith('$HEX[') and hex_string.endswith(']') and is_hexstring(hex_string[5:-1]):
        try:
            encoding_detection = chardet.detect(bytes.fromhex(hex_string[5:-1]))

            return bytes.fromhex(hex_string[5:-1]).decode(encoding_detection['encoding'])
        except Exception as e:
            return False
    else:
        return False


def str_to_hc_hex(string:str):
    try:
        return (f'$HEX[{string.encode("utf-8").hex()}]')

    except Exception as e:
        return False


if __name__ == '__main__':
    exit_code = 0
    parser = argparse.ArgumentParser()
    command_group = parser.add_mutually_exclusive_group(required=True)
    command_group.add_argument('-e', '--encode', help='Operation to encode a string', action='store_true')
    command_group.add_argument('-d', '--decode', help='Operation to decode a string', action='store_true')
    option_group = parser.add_argument('-s', '--string', help='String to en-/de-code', type=str, required=True)
    args = parser.parse_args()

    if args.encode:
        if (encoded := str_to_hc_hex(args.string)) is False:
            exit_code = 1
        else:
            print(encoded)

    if args.decode:
        if (decoded := hc_hex_to_str(args.string)) is False:
            exit_code = 1
        else:
            print(decoded)

    sys.exit(exit_code)
else:
    sys.exit(1)


# end of script
