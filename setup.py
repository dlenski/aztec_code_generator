#!/usr/bin/env python3
import sys
try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

if sys.version_info < (3,4):
    sys.exit("Python 3.4+ is required; you are using %s" % sys.version)

setup(name="aztec_code_generator",
      version="0.5",
      description='Aztec Code generator in Python',
      long_description=open('description.rst').read(),
      author='Dmitry Alimov',
      author_email="dvalimov@gmail.com",
      install_requires=open('requirements.txt').readlines(),
      extras_require={
          "Image": "pillow>=3.0",
      },
      tests_require=[
          "pillow>=3.0",
          "zxing",
      ],
      license='MIT',
      url="https://github.com/dlenski/aztec_code_generator",
      py_modules=["aztec_code_generator"],
      )
