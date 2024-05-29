#!/usr/bin/python
#  -*- coding: utf-8 -*-
import os
print(os.path.basename(__file__))
print(__file__)
print(os.path.splitext(__file__)[0] + '.log')
print(os.path.join(os.path.dirname(__file__), '..'))
print(os.path.dirname(os.path.realpath(__file__)))
print(os.path.abspath(os.path.dirname(__file__)))
