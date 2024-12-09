# hc-hex-stringer

Hashcat Hex Password Format Converter Utility

# Description and Example Usage:

Command-line help:
```
usage: hc-hex-stringer.py [-h] -s STRING (-e | -d)
```

You must specify a mode of operation (encode or decode) and a string against which to perform said operation.

To 'encode' a given string into Hashcat's 'hex' format:
```
# ./hc-hex-stringer.py --string 'marquee:' --encode
$HEX[6d6172717565653a]
```

To 'decode' a given hex string to (hopefully) printable text:
```
# ./hc-hex-stringer.py --string '$HEX[262333393a313539373533]' --decode
&#39:159753
```

# Signalling

Standard *nix-style messaging and exit codes apply:
* Exit code '0' for success.
* Exit code '1' for failure.

Efforts have been made to try to make this utility 'script-friendly' and generally easy to include into automation and scripted workflows.

# Prerequisites

Requires Python 3.x (preferably 3.7+) and uses the following (entirely standard) libraries:
* sys
* argparse
* chardet

# License

This tool is released under the Apache 2.0 license. See the LICENSE file in this repo for details.

# Built With

* [Python](https://www.python.org) designed by Guido van Rossum

## Author

**Rick Pelletier**
