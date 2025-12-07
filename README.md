# hc-hex-stringer

Hashcat Hex Password Format Converter Utility

# Prerequisites

Requires Python 3.x (preferably 3.11+) and uses the following libraries:
* annotations (future)
* argparse
* sys
* pathlib
* chardet

# Command-line help:
```
usage: hc-hex-stringer.py [-h] (-s STRING | -f FILE) (-e | -d) (--fast | --safe) [-i] [--verbose]

Hashcat $HEX[...] encoder/decoder (dual-path: safe / fast)

options:
  -h, --help            show this help message and exit
  -s STRING, --string STRING
                        String to encode or decode
  -f FILE, --file FILE  File containing one string per line to encode/decode
  -e, --encode          Encode to $HEX[...] format
  -d, --decode          Decode from $HEX[...] format
  --fast                Fast decode path: assume UTF-8 only (no chardet)
  --safe                Safe decode path: use chardet (recommended)
  -i, --ignore          Ignore decoding errors (per-line)
  --verbose             Show warnings on stderr (otherwise silent unless verbose)
```

Note: One option from each mutually exclusive set must be supplied.
  --encode and --decode are mutually exclusive options
  --file and --string are mutually exclusive options
  --fast and --safe are mutually exclusive options

# Example Usage:

To 'encode' a given string into Hashcat's 'hex' format:
```
# ./hc-hex-stringer.py --string 'marquee:' --encode --fast
$HEX[6d6172717565653a]
```

To 'decode' a given hex string to (hopefully) printable text:
```
# ./hc-hex-stringer.py --string '$HEX[262333393a313539373533]' --decode --safe
&#39:159753
```

A process-by-file option is available, assumes one string per line, and can be easily redirected to another file:
```
# ./hc-hex-stringer.py [ --encode | --decode ] [ --fast | --safe ] --file input_file.txt > output_file.txt
```

During this operations, any line that cannot be correctly en/decoded is skipped and no error message will be displayed. An override option is available to bypass this behavior.

# Caveats:

Some data encoded in this manner cannot be "decoded" in the conventional sense, particularly when 'chardet' cannot determine a viable character set use use. Binary data is a good example of "non-decodeable" data.

# Signalling

Standard *nix-style messaging and exit codes apply:
* Exit code '0' for success.
* Exit code '1' for failure.

Efforts have been made to try to make this utility 'script-friendly' and generally easy to integrate into automation and scripted workflows.

# License

This tool is released under the Apache 2.0 license. See the LICENSE file in this repo for details.

# Built With

* [Python](https://www.python.org) designed by Guido van Rossum

## Author

**Rick Pelletier**
