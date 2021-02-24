# Aztec Code generator

[![PyPI](https://img.shields.io/pypi/v/aztec_code_generator.svg)](https://pypi.python.org/pypi/aztec_code_generator)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/dlenski/aztec_code_generator/workflows/test_and_release/badge.svg)](https://github.com/dlenski/aztec_code_generator/actions?query=workflow%3Atest_and_release)

This is a pure-Python library to generate [Aztec Code](https://en.wikipedia.org/wiki/Aztec_code) 2D barcodes.

## Changelog

- `v0.1`-`v0.2`: initial Python packaging
- `v0.3`: allow optional border, more efficient matrix representation
- `v0.4`: merge https://github.com/delimitry/aztec_code_generator/pull/5 and fix tests
- `v0.5`:
  - code simplification
  - more efficient internal data structures (`Enum`)
  - encoding of `FLG(n)`
  - correct handling of Python 3 `str` vs. `bytes` (Aztec Code natively encodes _bytes_, not characters, and a reader's default interpretation of those bytes should be [ISO-8859-1 aka Latin-1](https://en.wikipedia.org/wiki/Iso-8859-1))
- `v0.6`:
  - more code simplification
  - make Pillow dependency optional
  - add `print_fancy` for UTF-8 output (inspired by `qrencode -t ansiutf8`)
  - bugfix for `DIGIT`→`PUNCT` transition (and add missed test case)
  - allow customization of error correction percentage level


## Installation

Releases [from PyPi](https://pypi.org/project/aztec-code-generator/) may be installed with `pip3 install aztec_code_generator`.

Bleeding-edge version from `master` branch of this repository can be installed with
`pip3 install https://github.com/dlenski/aztec_code_generator/archive/master.zip`.

### Dependencies

[Pillow](https://pillow.readthedocs.io) (Python image generation library) is required if you want to generate image objects and files.

## Usage

### Creating and encoding

```python
from aztec_code_generator import AztecCode
data = 'Aztec Code 2D :)'
aztec_code = AztecCode(data)
```

The `AztecCode()` constructor takes additional, optional arguments:

- `size` and `compact`: to set a specific symbol size (e.g. `19, True` for a compact 19×19 symbol); see `keys(aztec_code_generator.configs)` for possible values
- `ec_percent` for error correction percentage (default is the recommended 23), plus `size` a

### Saving an image file

`aztec_code.save('aztec_code.png', module_size=4, border=1)` will save an image file `aztec_code.png` of the symbol, with 4×4 blocks of white/black pixels in
the output, and with a 1-block border.

![Aztec Code](https://1.bp.blogspot.com/-OZIo4dGwAM4/V7BaYoBaH2I/AAAAAAAAAwc/WBdTV6osTb4TxNf2f6v7bCfXM4EuO4OdwCLcB/s1600/aztec_code.png "Aztec Code with data")

### Creating an image object

`aztec_code.image()` will yield a monochrome-mode [PIL `Image` object](https://pillow.readthedocs.io/en/stable/reference/Image.html) representing the image
in-memory. It also accepts optional `module_size` and `border`.

### Text-based output

`aztec_code.print_fancy()` will print the resulting Aztec Code to standard output using
[Unicode half-height block elements](https://en.wikipedia.org/wiki/Block_Elements) encoded
with UTF-8 and ANSI color escapes. It accepts optional `border`.

`aztec_code.print_out()` will print out the resulting Aztec Code to standard
output as plain ASCII text, using `#` and ` ` characters:

```
##  # ## ####
 #   ## #####  ### 
 #  ##  # #   # ###
## #  #    ## ##   
    ## # #    # #  
## ############ # #
 ### #       ###  #
##   # ##### # ## #
 #   # #   # ##    
 # # # # # # ###   
    ## #   # ## ## 
#### # ##### ## #  
  # ##       ## ## 
 ##  ########### # 
  ##    # ##   ## #
     ## # ### #  ##
      ############ 
##   #     # ##   #
##  #    ## ###   #
```

## Authors:

Originally written by [Dmitry Alimov (delimtry)](https://github.com/delimitry).

Updates, bug fixes, Python 3-ification, and careful `bytes`-vs.-`str` handling
by [Daniel Lenski (dlenski)](https://github.com/dlenski).

## License:

Released under [The MIT License](https://github.com/delimitry/aztec_code_generator/blob/master/LICENSE).
