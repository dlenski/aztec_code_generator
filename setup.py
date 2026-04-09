#!/usr/bin/env python3
import sys
try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

if sys.version_info < (3, 7):
    sys.exit("Python 3.7+ is required; you are using %s" % sys.version)

setup(name="aztec_code_generator",
      version="0.11",
      description='Aztec Code generator in Python',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      author='Dmitry Alimov',
      author_email="dvalimov@gmail.com",
      maintainer='Daniel Lenski',
      maintainer_email='dlenski@gmail.com',
      install_requires=open('requirements.txt').readlines(),
      extras_require={
          "Image": [
              "pillow>=8.0",
          ]
      },
      tests_require=open('requirements-test.txt').readlines(),
      license='MIT',
      url="https://github.com/dlenski/aztec_code_generator",
      py_modules=["aztec_code_generator"],
      )
