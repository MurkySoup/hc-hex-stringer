#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Hashcat Hex Password Format Converter, Version 0.8.1-Beta (Do Not Distribute)
By Rick Pelletier (galiagante@gmail.com), 25 September 2022
Last update: 02 January 2025

Help:

usage: hc-hex-stringer.py [-h] (-s STRING | -f FILE) (-e | -d)

options:
  -h, --help                    show this help message and exit
  -s STRING, --string STRING    string to en-/de-code
  -f FILE, --file FILE          file to en-/de-code
  -e, --encode                  encode to hc hex format
  -d, --decode                  decode from hc hex format


Example usage:

# ./hc-hex-stringer.py --string 'marquee:' --encode
$HEX[6d6172717565653a]

# ./hc-hex-stringer.py --string '$HEX[262333393a313539373533]' --decode
&#39:159753


In the event of an encoding or decoding error (for example, chardet could not
identify the correct character set to perform a conversion), nothing will be
displayed, but an exit code of '1' will be returned to the O/S. Successful
en/decoding will return the converted string and an exit code of '0'.

An option to process entire files and assumes one string per line. Lines that
cannot be properly encoded or decoded are skipped. The focus is on task
completion, rather than halting an every error.
"""


import sys
import argparse
import chardet
from pathlib import Path


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


def process_file(input_filename:str, mode:str):
    try:
        with open(input_filename, 'r') as ifp:
            for line in ifp:
                if mode == 'encode':
                    if (conversion := str_to_hc_hex(line.rstrip())) is False:
                        continue

                if mode == 'decode':
                    if (conversion := hc_hex_to_str(line.rstrip())) is False:
                        continue

                print(conversion)

        ifp.close()

    except Exception as e:
        print(e)
        return False

    return True


def file_exists(filename:str):
    try:
        abs_path = Path(filename).resolve(strict=True)
    except FileNotFoundError as e:
        print(e)

        return False

    return True


if __name__ == '__main__':
    exit_code = 0
    parser = argparse.ArgumentParser()

    command_group_one = parser.add_mutually_exclusive_group(required=True)
    command_group_one.add_argument('-s', '--string', help='string to en-/de-code', type=str)
    command_group_one.add_argument('-f', '--file',   help='file to en-/de-code', type=str)

    command_group_two = parser.add_mutually_exclusive_group(required=True)
    command_group_two.add_argument('-e', '--encode', help='encode to hc hex format',   action='store_true')
    command_group_two.add_argument('-d', '--decode', help='decode from hc hex format', action='store_true')

    args = parser.parse_args()

    if args.file:
        if file_exists(args.file) is False:
            exit_code = 1
        else:
            if args.encode:
                if process_file(args.file, 'encode') is False:
                    exit_code = 1
            if args.decode:
                if process_file(args.file, 'decode') is False:
                    exit_code = 1


    if args.string:
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
