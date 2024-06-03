#!/usr/bin/python
#  -*- coding: utf-8 -*-

import docker
import os
import os.path
from src.utils import git_checkout, git_branch, docker_compose, run
from src.promoted_image import PromoteImage
from src.results_iterator import ResultsIteratorForDockerCompose


class Project:
    def __init__(self, directory, branch):
        self.directory = directory
        self.project_dir = os.path.abspath(directory)
        folder = os.path.basename(self.project_dir)
        self.workspace = os.path.join(self.project_dir, f'workspace.{folder}')
        self.versions_dir = os.path.join(self.workspace, '.versions')
        self.branch = branch
    
    def get_dir(self):
        return self.directory

    def get_workspace(self):
        return self.workspace

    def get_versions(self):
        return self.versions_dir
    
    def validate(self):
        # verify '.git' exists in current directory
        if not os.path.exists(self.project_dir) or not os.path.exists(self.workspace):
            raise ValueError('Must execute this script from a deployment folder, or specify a directory to work from')
        if not os.path.exists(os.path.join(self.project_dir, '.git')):
            raise ValueError('Must execute this script from a GIT folder')
        if not os.path.exists(os.path.join(self.workspace, 'docker-compose.yml')):
            raise ValueError('No "docker-compose.yml" detected')
        if not os.path.exists(f'{self.versions_dir}/.git'):
            raise ValueError('Must execute this script from a deployment folder')

        if self.branch != None:
            git_checkout(self.project_dir, self.branch)
        else:
            self.branch = git_branch(self.project_dir)

        client = docker.from_env()
        if not client:
            raise ValueError('Must have DOCKER running')


    def promote(self):
        ResultsIteratorForDockerCompose.DEV_BRANCH = self.branch
        PromoteImage.set_globals()
        images = []
        for image in docker_compose(self.workspace):
            try:
                while image not in images:
                    promoted_image = PromoteImage(image)
                    promoted_image.promote(self.branch)
                    images.append(image)
                    image = promoted_image.parent()
            except Exception as e:
                print(e.with_traceback(e.__traceback__))
        # update versions folder
        git_checkout(self.versions_dir, 'main')
        run(f'git reset --hard origin/{self.branch}', self.versions_dir, None)
        run('git push', self.versions_dir, None)

        # update project folder
        git_checkout(self.directory, 'main')
        run(f'git reset --hard origin/{self.branch}', self.directory, None)
        run('git push', self.directory, None)
        


    def update(self):
        pass
