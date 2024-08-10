#!/usr/bin/python
#  -*- coding: utf-8 -*-

import docker
import os
import os.path
from src.color import color
from src.utils import git_checkout, git_branch, docker_compose, run
from src.promote_image import PromoteImage
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

        self.client = docker.APIClient(base_url='unix://var/run/docker.sock')
        if not self.client:
            raise ValueError('Must have DOCKER running')


    def promote(self):
        ResultsIteratorForDockerCompose.DEV_BRANCH = self.branch
        PromoteImage.set_globals(self.client)
        promoted_images = []
        primary_images = []
        for image in docker_compose(self.workspace):
            rep = image['Repository']
            print(color.change("BLUE", f'\nProcessing {rep} ========================================================================'))
            primary_images.append(f'{rep}:{PromoteImage.PROMOTED_BRANCH}')
            PromoteImage.images_to_remove.append(f'{rep}:{self.branch}')
            try:
                while image not in promoted_images:
                    promoted_image = PromoteImage(image, self.branch)
                    promoted_image.promote()
                    promoted_images.append(image)
                    image = promoted_image.get_parent()
                    if image == None:
                        break
            except Exception as e:
                print(e.with_traceback(e.__traceback__))
            print('')
        PromoteImage.remove_images(primary_images)
        
        # update versions folder
        print(color.change("BLUE", f'\ncd {self.versions_dir}'))
        git_checkout(self.versions_dir, self.branch)
        run('git pull', self.versions_dir, None)
        run(f'git push --force origin HEAD:{PromoteImage.PROMOTED_BRANCH}', self.versions_dir, None)
        run(f'git checkout {PromoteImage.PROMOTED_BRANCH}', self.versions_dir, None)
        run(f'git reset --hard origin/{PromoteImage.PROMOTED_BRANCH}', self.versions_dir, None)

        # update project folder
        print(color.change("BLUE", f'\ncd {self.directory}'))
        git_checkout(self.directory, self.branch)
        run('git pull', self.directory, None)
        run(f'git push --force origin HEAD:{PromoteImage.PROMOTED_BRANCH}', self.directory, None)
        run(f'git checkout {PromoteImage.PROMOTED_BRANCH}', self.directory, None)
        run(f'git reset --hard origin/{PromoteImage.PROMOTED_BRANCH}', self.directory, None)
        

    def update(self):
        ResultsIteratorForDockerCompose.DEV_BRANCH = self.branch
        PromoteImage.set_globals(self.client)
        print(color.change("BLUE", f'\ncd {self.versions_dir}'))
        git_checkout(self.versions_dir, self.branch)
        run('git pull', self.versions_dir, None)

        print(color.change("BLUE", f'\ncd {self.directory}'))
        git_checkout(self.directory, self.branch)
        run('git pull', self.directory, None)
