#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Hashcat Hex Password Format Converter, Version 0.5-Beta (Do Not Distribute)
By Rick Pelletier (galiagante@gmail.com), 25 September 2022
Last update: 27 September 2022

Example usage:

# ./hc-hex-stringer.py --string 'marquee:' --encode
$HEX[6d6172717565653a]

# ./hc-hex-stringer.py --string '$HEX[262333393a313539373533]' --decode
&#39:159753
"""


import sys
import argparse


def is_hexstring(string:str):
  try:
    for s in string:
      int(s, 16)

    return True
  except:
    return False


def hc_hex_to_str(string:str):
  if string.startswith('$HEX[') and string.endswith(']') and is_hexstring(string[5:-1]):
    try:
      return(f'{bytes.fromhex(string[5:-1]).decode("utf-8")}')
    except:
      return False
  else:
    return False


def str_to_hc_hex(string:str):
  return(f'$HEX[{string.encode("utf-8").hex()}]')


if __name__ == '__main__':
  exit_code = 0
  parser = argparse.ArgumentParser()
  command_group = parser.add_mutually_exclusive_group(required = True)
  command_group.add_argument('-e', '--encode', help = 'Operation to encode a string', action = 'store_true')
  command_group.add_argument('-d', '--decode', help = 'Operation to decode a string', action = 'store_true')
  option_group = parser.add_argument('-s', '--string', help = 'String to en-/de-code', type = str, required = True)
  args = parser.parse_args()

  if args.encode:
    encoded = str_to_hc_hex(args.string)
    print(f'{encoded}', file = sys.stdout)

  if args.decode:
    decoded = hc_hex_to_str(args.string)

    if decoded is not False:
      print(f'{decoded}', file = sys.stdout)
    else:
      print('Error decoding string', file = sys.stderr)
      exit_code = 1

  sys.exit(exit_code)
else:
  sys.exit(1)

# end of script
