Aztec Code generator in Python

Dependencies
------------
Pillow - Python Imaging Library


Usage
-----

.. code:: python

    data = 'Aztec Code 2D :)'
    aztec_code = AztecCode(data)
    aztec_code.save('aztec_code.png', module_size=4)

This code will generate an image file ``aztec_code.png`` of an Aztec Code containing the text "Aztec Code 2D :)".

.. image:: https://1.bp.blogspot.com/-OZIo4dGwAM4/V7BaYoBaH2I/AAAAAAAAAwc/WBdTV6osTb4TxNf2f6v7bCfXM4EuO4OdwCLcB/s1600/aztec_code.png
    :alt: Aztec Code with data

.. code:: python

    data = 'Aztec Code 2D :)'
    aztec_code = AztecCode(data)
    aztec_code.print_out()

This code will print out the resulting 19×19 (compact) Aztec Code to standard output as text.

::

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


Authors
-------

Written by `Dmitry Alimov (delimtry) <https://github.com/delimitry>`__ and packaged by `Daniel Lenski (dlenski) <https://github.com/dlenski>`__.


License
-------

Released under `The MIT License <https://github.com/dlenski/aztec_code_generator/blob/master/LICENSE>`__.
