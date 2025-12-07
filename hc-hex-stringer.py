#!/usr/bin/env python3

"""
Hashcat Hex Password Format Converter, Version 1.0-Beta (Do Not Distribute)
By Rick Pelletier (galiagante@gmail.com), 25 September 2022
Last update: 07 December 2025

Help:

usage: hc-hex-stringer.py [-h] [-i] (-s STRING | -f FILE) (-e | -d)

options:
  -h, --help                    show this help message and exit
  -s STRING, --string STRING    string to en-/de-code
  -f FILE, --file FILE          file to en-/de-code
  -e, --encode                  encode to hc hex format
  -d, --decode                  decode from hc hex format
  -i, --ignore                  ignore decoding errors

Example usage:

# ./hc-hex-stringer.py --string 'marquee:' --encode
$HEX[6d6172717565653a]

# ./hc-hex-stringer.py --string '$HEX[262333393a313539373533]' --decode
&#39:159753


Successful en/decoding will return the converted string and an exit code of '0'.

In the event of an encoding or decoding error (for example, chardet could not
identify the correct character set to perform a conversion), nothing will be
displayed, but an exit code of '1' will be returned to the O/S. In the event
that errors are bypassed via '--ignore' option, the return value will always
be '0'.

An option to process entire files has been included and assumes one string per
line. Lines that cannot be properly encoded or decoded are skipped (unless
'--ignore' is used). The focus is on task completion, rather than halting on
and/or reporting every error.

Linter: ruff check hc-hex-stringer.py --extend-select F,B,UP
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path
import chardet

# =====================================================================
# Utility Functions
# =====================================================================

def is_hex_string(s: str) -> bool:
    """
    Return True if `s` is a valid even-length hexadecimal string.
    """
    if len(s) % 2 != 0:
        return False

    try:
        bytes.fromhex(s)
        return True
    except ValueError:
        return False

def hc_hex_to_str(hex_string: str, ignore_errors: bool = False) -> str | None:
    """
    Decode a Hashcat-style $HEX[...] string into a normal UTF-8 string.

    Parameters
    ----------
    hex_string : str
        Input string in Hashcat hex format.
    ignore_errors : bool
        If True, decoding errors are ignored.

    Returns
    -------
    Optional[str]
        Decoded string, or None on failure.
    """

    if (
        hex_string.startswith("$HEX[")
        and hex_string.endswith("]")
        and is_hex_string(hex_string[5:-1])
    ):
        hex_body = hex_string[5:-1]
        raw_bytes = bytes.fromhex(hex_body)

        detection = chardet.detect(raw_bytes)
        encoding = detection.get("encoding") or "utf-8"
        errors_mode = "ignore" if ignore_errors else "strict"

        try:
            return raw_bytes.decode(encoding, errors=errors_mode)
        except UnicodeDecodeError:
            return None

    return None

def str_to_hc_hex(s: str) -> str:
    """
    Encode a string into Hashcat's $HEX[...] format (UTF-8 encoded).
    """
    hex_value = s.encode("utf-8").hex()

    return f"$HEX[{hex_value}]"

# =====================================================================
# File Processing
# =====================================================================

def process_file(input_file: Path, mode: str, ignore_errors: bool = False) -> bool:
    """
    Process an entire file line-by-line for encoding or decoding.

    Parameters
    ----------
    input_file : Path
        File to process.
    mode : str
        Either "encode" or "decode".
    ignore_errors : bool
        If True, ignore decode errors.

    Returns
    -------
    bool
        True on success, False on failure.
    """

    try:
        with input_file.open("r", encoding="utf-8", errors="ignore") as f:
            for raw_line in f:
                line = raw_line.rstrip("\n")

                if mode == "encode":
                    print(str_to_hc_hex(line))
                    continue

                if mode == "decode":
                    decoded = hc_hex_to_str(line, ignore_errors=ignore_errors)
                    if decoded is not None:
                        print(decoded)
                    elif not ignore_errors:
                        return False

        return True

    except Exception:
        return False

# =====================================================================
# CLI Interface
# =====================================================================

def build_arg_parser() -> argparse.ArgumentParser:
    """
    Configure CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description="Hashcat HEX Format Encoder/Decoder",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    src_group = parser.add_mutually_exclusive_group(required=True)
    src_group.add_argument("-s", "--string", help="String to encode or decode", type=str)
    src_group.add_argument("-f", "--file", help="File to encode or decode", type=str)

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("-e", "--encode", help="Encode into $HEX[...] format", action="store_true")
    mode_group.add_argument("-d", "--decode", help="Decode from $HEX[...] format", action="store_true")

    parser.add_argument("-i", "--ignore", help="Ignore decode errors", action="store_true")

    return parser

# =====================================================================
# Main Execution
# =====================================================================

def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    # -----------------------------------------------------------------
    # File Mode
    # -----------------------------------------------------------------
    if args.file:
        target = Path(args.file)

        if not target.exists():
            return 1

        mode = "encode" if args.encode else "decode"
        ok = process_file(target, mode=mode, ignore_errors=args.ignore)

        return 0 if ok or args.ignore else 1

    # -----------------------------------------------------------------
    # String Mode
    # -----------------------------------------------------------------
    if args.string:
        if args.encode:
            print(str_to_hc_hex(args.string))

            return 0

        if args.decode:
            decoded = hc_hex_to_str(args.string, ignore_errors=args.ignore)

            if decoded is None and not args.ignore:
                return 1

            print(decoded or "")

            return 0

    return 1

# =====================================================================

if __name__ == "__main__":
    sys.exit(main())

# end of script
