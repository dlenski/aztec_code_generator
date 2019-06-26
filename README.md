# Aztec Code generator

[![PyPI](https://img.shields.io/pypi/v/aztec_code_generator.svg)](https://pypi.python.org/pypi/aztec_code_generator)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://api.travis-ci.org/dlenski/aztec_code_generator.png)](https://travis-ci.org/dlenski/aztec_code_generator)

Aztec Code generator in Python

## Dependencies:  

PIL - Python Imaging Library (or Pillow)

## Usage:
```python
data = 'Aztec Code 2D :)'
aztec_code = AztecCode(data)
aztec_code.save('aztec_code.png', module_size=4)
```

This code will generate an image file `aztec_code.png` of an Aztec Code containing the text "Aztec Code 2D :)".

![Aztec Code](https://1.bp.blogspot.com/-OZIo4dGwAM4/V7BaYoBaH2I/AAAAAAAAAwc/WBdTV6osTb4TxNf2f6v7bCfXM4EuO4OdwCLcB/s1600/aztec_code.png "Aztec Code with data")

```python
data = 'Aztec Code 2D :)'
aztec_code = AztecCode(data)
aztec_code.print_out()
```

This code will print out the resulting 19×19 (compact) Aztec Code to standard output as text.

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

Written by [Dmitry Alimov (delimtry)](https://github.com/delimitry)
and packaged by [Daniel Lenski (dlenski)](https://github.com/dlenski).

## License:

Released under [The MIT License](https://github.com/delimitry/aztec_code_generator/blob/master/LICENSE).
