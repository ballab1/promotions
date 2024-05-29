#!/usr/bin/python
#  -*- coding: utf-8 -*-

"""
promote

    promote images which we have built

"""

import command
import shlex
from .src import color, ResultsIteratorForDockerCompose, ResultsIteratorForText


BRANCH = 'dev'

def docker_compose(workspace):
    return run('docker-compose images --format json', workspace, ResultsIteratorForDockerCompose)

def git_branch(project_dir):
    return run('git rev-parse --abbrev-ref HEAD', project_dir, ResultsIteratorForText)[0]

def git_checkout(project_dir, branch):
    run(f'git checkout {branch}', project_dir, None)

def git_last_commit_message(project_dir):
    return run('git log -1 --format=%s', project_dir, ResultsIteratorForText)[0]

def run(cmdline, directory, fn):
    print(color.change(color.GREY, cmdline))
    response = command.run(shlex.split(cmdline), cwd = directory)
    if fn == None:
        return response.exit
    results = []
    if response.exit == 0:
        for val in fn(response.output.decode('ascii')):
            results.append(val)
    return results
