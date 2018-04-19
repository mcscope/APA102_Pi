#!/usr/bin/env python

from distutils.core import setup

setup(name='liteup',
      version='0.2',
      description='APA102 LED colorschemes client and flask webserver',
      author='Chris Beacham',
      author_email='mcscope@gmail.com',
      url='https://github.com/mcscope/liteup/',
      packages=['liteup'],
      install_requires=[
          "ConfigArgParse",
          "requests",
          "flask",
          "aiohttp",
          "spidev",
          "attrs",
          "numpy",
          "scipy"
      ]
      )
