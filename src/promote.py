#!/usr/bin/python
#  -*- coding: utf-8 -*-

"""
promote

    promote images which we have built

"""

from src import BRANCH, git_branch, docker_compose 
import docker

class Promote:
    def __init__(self):
        self.client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    # VERIFY git branch 'dev' is checked out
    # get last commit message
    # GET list of container images and their dependant images
    # rename images and push both main & fingerprint to registry
    # reset 'main' to origin/dev
    # update 'versions' repo
    # update initial repo

    def main(self, args):
        branch = git_branch(args.project_dir)
        if branch != BRANCH:
           raise ValueError('Wrong branch detected')
        images = []
        for image in docker_compose(args.workspace):
            images.append(image)
