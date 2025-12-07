#!/usr/bin/env python3

"""
Hashcat Hex Password Format Converter, Version 1.1-Beta (Do Not Distribute)
By Rick Pelletier (galiagante@gmail.com), 25 September 2022
Last update: 07 December 2025

Usage: hc-hex-stringer.py [-h] (-s STRING | -f FILE) (-e | -d) [-i] [--fast] [--safe] [--verbose]

Hashcat $HEX[...] encoder/decoder (dual-path: safe (default) / fast)

options:
  -h, --help                  show this help message and exit
  -s STRING, --string STRING  String to encode or decode
  -f FILE, --file FILE        File containing one string per line to encode/decode
  -e, --encode                Encode to $HEX[...] format
  -d, --decode                Decode from $HEX[...] format
  -i, --ignore                Ignore decoding errors (per-line)
  --fast                      Fast decode path: assume UTF-8 only (no chardet)
  --safe                      Safe decode path: use chardet (recommended)
  --verbose                   Show warnings on stderr (otherwise silent unless verbose)

Note: One option from each mutually exclusive set must be supplied.
  --encode and --decode are mutually exclusive options
  --file and --string are mutually exclusive options
  --fast and --safe are mutually exclusive options

Example usage:

# ./hc-hex-stringer.py --string 'marquee:' --encode --safe
$HEX[6d6172717565653a]

# ./hc-hex-stringer.py --string '$HEX[262333393a313539373533]' --decode --fast
&#39:159753

Linter: ruff check hc-hex-stringer.py --extend-select F,B,UP
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path
import chardet

# ---------------------------
# Utility functions
# ---------------------------

def is_hex_string(s: str) -> bool:
    """
    Return True if `s` is a valid even-length hexadecimal string.
    """
    if len(s) % 2 != 0:
        return False
    try:
        # bytes.fromhex will raise ValueError on non-hex characters
        bytes.fromhex(s)

        return True
    except ValueError:
        return False

def warn(message: str, verbose: bool) -> None:
    """
    Print a warning to stderr if verbose is True.
    """
    if verbose:
        sys.stderr.write(f"[WARN] {message}\n")

# ---------------------------
# Encoding / Decoding core
# ---------------------------

def str_to_hc_hex(s: str) -> str:
    """
    Encode a unicode string into Hashcat $HEX[...] representation using UTF-8.
    """
    return f"$HEX[{s.encode('utf-8').hex()}]"

def decode_using_safe(raw_bytes: bytes, ignore_errors: bool, verbose: bool) -> str | None:
    """
    Safe decode path: use chardet to detect encoding, then decode accordingly.
    Returns the decoded string on success, or None on failure.
    """
    detection = chardet.detect(raw_bytes)
    encoding = detection.get("encoding")
    confidence = detection.get("confidence", 0.0)

    # If chardet failed to return an encoding, default to utf-8
    if not encoding:
        warn("chardet failed to detect encoding; attempting UTF-8.", verbose)
        encoding = "utf-8"

    # Warn if detected encoding is not UTF-8 (possible non-UTF-8 data)
    if encoding.lower() != "utf-8":
        warn(f"Detected encoding '{encoding}' (confidence={confidence}). "
             "This is likely non-UTF-8 data.", verbose)

    errors_mode = "ignore" if ignore_errors else "strict"

    try:
        return raw_bytes.decode(encoding, errors=errors_mode)
    except (LookupError, UnicodeDecodeError) as exc:
        # LookupError: unknown codec name returned by chardet (very rare)
        # UnicodeDecodeError: strict decode failure
        warn(f"Safe decode failed: {exc}", verbose)

        return None

def decode_using_fast(raw_bytes: bytes, ignore_errors: bool, verbose: bool) -> str | None:
    """
    Fast decode path: assume UTF-8 only. If strict decoding fails and ignore_errors is False,
    return None. If ignore_errors is True, decode with errors='ignore' and warn.
    """
    try:
        return raw_bytes.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        # If the caller requested ignoring errors, produce a best-effort decode
        if ignore_errors:
            warn("UTF-8 strict decode failed; using errors='ignore' to produce best-effort output.", verbose)
            return raw_bytes.decode("utf-8", errors="ignore")
        warn("UTF-8 strict decode failed and --ignore not set; skipping.", verbose)

        return None


def hc_hex_to_str(hex_string: str, fast: bool = False, ignore_errors: bool = False, verbose: bool = False) -> str | None:
    """
    Convert a $HEX[...] string to a decoded Unicode string.

    Returns:
        Decoded string on success, or None on failure.
    """
    if not (hex_string.startswith("$HEX[") and hex_string.endswith("]")):
        warn("Input does not appear to be $HEX[...] format.", verbose)
        return None

    hex_body = hex_string[5:-1]

    if not is_hex_string(hex_body):
        warn("Content inside $HEX[...] is not valid hex.", verbose)
        return None

    raw_bytes = bytes.fromhex(hex_body)

    if fast:
        return decode_using_fast(raw_bytes, ignore_errors=ignore_errors, verbose=verbose)

    return decode_using_safe(raw_bytes, ignore_errors=ignore_errors, verbose=verbose)

# ---------------------------
# File processing
# ---------------------------

def process_file(input_path: Path, mode: str, fast: bool, ignore_errors: bool, verbose: bool) -> bool:
    """
    Process an input file line-by-line.

    mode: 'encode' or 'decode'
    fast: whether to use the fast (UTF-8-only) decoder
    ignore_errors: whether to ignore per-line decode errors
    verbose: whether to print warnings to stderr

    Returns True on overall success (or when ignore_errors=True even if some lines failed).
    Returns False on failure when ignore_errors=False and at least one line failed.
    """
    if mode not in {"encode", "decode"}:
        raise ValueError("mode must be 'encode' or 'decode'")

    try:
        # Read as raw text (we treat each line as a logical input; encoding of file itself is not assumed)
        with input_path.open("r", encoding="utf-8", errors="surrogateescape") as fh:
            had_failure = False
            for lineno, raw_line in enumerate(fh, start=1):
                line = raw_line.rstrip("\n\r")

                if mode == "encode":
                    print(str_to_hc_hex(line))
                    continue

                # decode mode
                decoded = hc_hex_to_str(line, fast=fast, ignore_errors=ignore_errors, verbose=verbose)
                if decoded is None:
                    had_failure = True
                    # In ignore mode, skip problematic line(s) silently (or with warnings if verbose)
                    if ignore_errors:
                        warn(f"Skipping line {lineno} (decode failed).", verbose)
                        continue
                    # Not in ignore mode: fail early (stop processing)
                    warn(f"Line {lineno} failed to decode; aborting (use --ignore to continue).", verbose)
                    return False
                print(decoded)

            # If any lines failed but ignore_errors was set, that's considered success
            if had_failure and not ignore_errors:
                return False

        return True
    except FileNotFoundError:
        warn(f"File not found: {input_path}", verbose)
        return False
    except PermissionError:
        warn(f"Permission error while opening file: {input_path}", verbose)
        return False
    except Exception as exc:
        warn(f"Unhandled exception while processing file: {exc}", verbose)
        return False

# ---------------------------
# CLI
# ---------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Hashcat $HEX[...] encoder/decoder (dual-path: safe / fast)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    src_group = parser.add_mutually_exclusive_group(required=True)
    src_group.add_argument("-s", "--string", help="String to encode or decode", type=str)
    src_group.add_argument("-f", "--file", help="File containing one string per line to encode/decode", type=str)

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("-e", "--encode", help="Encode to $HEX[...] format", action="store_true")
    mode_group.add_argument("-d", "--decode", help="Decode from $HEX[...] format", action="store_true")

    chardet_group = parser.add_mutually_exclusive_group(required=True)
    chardet_group.add_argument("--fast", help="Fast decode path: assume UTF-8 only (no chardet)", action="store_true")
    chardet_group.add_argument("--safe", help="Safe decode path: use chardet (default)", action="store_true")

    parser.add_argument("-i", "--ignore", help="Ignore decoding errors (per-line)", action="store_true")
    parser.add_argument("--verbose", help="Show warnings on stderr (otherwise silent unless verbose)", action="store_true")

    return parser

def main(argv: list[str] | None = None) -> int:
    """
    Main entry point. Returns 0 on success, non-zero on failure.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    fast_mode = bool(args.fast)
    # If --safe explicitly provided, ensure fast_mode False.
    if args.safe:
        fast_mode = False

    ignore_errors = bool(args.ignore)
    verbose = bool(args.verbose)

    # File mode
    if args.file:
        path = Path(args.file)
        mode = "encode" if args.encode else "decode"
        ok = process_file(path, mode=mode, fast=fast_mode, ignore_errors=ignore_errors, verbose=verbose)

        # If ignore_errors was set, always exit 0 as per previous behavior
        if ignore_errors:
            return 0

        return 0 if ok else 1

    # String mode
    if args.string is not None:
        if args.encode:
            print(str_to_hc_hex(args.string))

            return 0

        # decode single string
        decoded = hc_hex_to_str(args.string, fast=fast_mode, ignore_errors=ignore_errors, verbose=verbose)

        if decoded is None:
            if ignore_errors:
                # Print nothing but exit 0 (preserve prior behavior)
                return 0
            # On failure and not ignoring, exit with error and no output
            return 1

        print(decoded)

        return 0

    # Shouldn't reach here (argparse handles required groups)
    return 1

if __name__ == "__main__":
    sys.exit(main())

# end of script
