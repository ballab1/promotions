#!/usr/bin/python3
#  -*- coding: utf-8 -*-

################################################################################
# Copyright (c) 2022-2023 Dell Inc. or its subsidiaries.  All rights reserved.
################################################################################

#
#  utility that can be used to generate color strings on terminal
#

# ansi color codes
class color:
    no_color = False
    values = {'RESET':   '\33[0m',
              'black':   '\33[30m', 'default': '\33[39m',
              'BLUE':    '\33[94m', 'blue':    '\33[34m',
              'CYAN':    '\33[96m', 'cyan':    '\33[36m',
              'GRAY':    '\33[90m', 'gray':    '\33[37m',
              'GREY':    '\33[90m', 'grey':    '\33[37m',
              'GREEN':   '\33[92m', 'green':   '\33[32m',
              'MAGENTA': '\33[95m', 'magenta': '\33[35m',
              'RED':     '\33[91m', 'red':     '\33[31m',
              'WHITE':   '\33[97m', 'white':   '\33[39m',
              'YELLOW':  '\33[93m', 'yellow':  '\33[33m'}

    @staticmethod
    def change(a_color, a_str):
        if color.no_color or a_color not in color.values:
           return a_str
        clr = color.values[a_color]
        rst = color.values['RESET']
        return f'{clr}{a_str}{rst}'

    @staticmethod
    def ERROR():
        return color.change('RED', '* * * ERROR:')

    @staticmethod
    def PASS(msg):
        clr = color.change('GREEN', '* * * PASS: ')
        return f'{clr}{msg}'

