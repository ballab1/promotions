#!/usr/bin/python
#  -*- coding: utf-8 -*-

"""
promote

    promote images which we have built

"""

import argparse
import sys
from src.color import color
from src.project import Project


class GetArgs:
    def __init__(self, usage):
         # parse any command line arguments
        p = argparse.ArgumentParser(description='update/promote content',
                                    epilog=usage(),
                                    formatter_class=argparse.RawDescriptionHelpFormatter)
        p.add_argument('-b', '--branch', required=False, help='development branch')
        p.add_argument('-d', '--directory', required=False, help='workspace directory', default='.')
        p.add_argument('-u', '--update', required=False, help='update workspace')
        p.add_argument('-p', '--promote', required=False, help='promote workspace and docker images')

        args = p.parse_args()
        self.promote = args.promote
        self.update = args.update
        if len(sys.argv) == 1:
            self.update = True
        print(color.change("WHITE", f'Current directory: {args.directory}'))
        self.project = Project(args.directory, args.branch)

    def validate_options(self):
        if self.promote == self.update:
            raise ValueError('Options must not be the same')
        self.project.validate()
