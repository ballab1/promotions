#!/usr/bin/python
#  -*- coding: utf-8 -*-

"""
promote

    promote images which we have built

"""

from src import App
import sys


def usage():
    examples = """

Usage:
    $progname [ -h | --help ]
              [ -d | --directory ]
              [ -p | --promote }
              [ -u | --update ]

    Common options:
        -h --help                  Display a basic set of usage instructions
        -d --directory             workspace directory
        -p --project <project>     promote workspace and docker images
        -u --update                update workspace

"""
    return examples

if __name__ == '__main__':
    app = App()
    sys.exit(app.main())
