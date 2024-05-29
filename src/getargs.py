#!/usr/bin/python
#  -*- coding: utf-8 -*-

"""
promote

    promote images which we have built

"""

import argparse
import docker
import os
import os.path
import sys
from src import BRANCH, git_checkout, git_branch, usage


class GetArgs:
    def __init__(self):
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
        self.branch = args.branch
        self.directory = args.directory
        if len(sys.argv) == 1:
            self.update = True
        self.project_dir = os.path.abspath(args.directory)
        folder = os.path.basename(self.project_dir)
        self.workspace = os.path.join(self.project_dir, f'workspace.{folder}')

    def validate_options(self):
        if self.promote == self.update:
            raise ValueError('Options must not be the same')
        # verify '.git' exists in current directory
        if not os.path.exists(self.project_dir) or not os.path.exists(self.workspace):
            raise ValueError('Must execute this script from a deployment folder, or specify a directory to work from')
        if not os.path.exists(os.path.join(self.project_dir, '.git')):
            raise ValueError('Must execute this script from a GIT folder')
        if not os.path.exists(os.path.join(self.workspace, 'docker-compose.yml')):
            raise ValueError('No "docker-compose.yml" detected')
        if not os.path.exists(f'{self.workspace}/.versions/.git'):
            raise ValueError('Must execute this script from a deployment folder')
        if self.branch:
            git_checkout(self.project_dir, self.branch)
        else:
            self.branch = git_branch(self.project_dir)
        global BRANCH
        BRANCH = self.branch
        client = docker.from_env()
        if not client:
            raise ValueError('Must have DOCKER running')
        self.client = client
