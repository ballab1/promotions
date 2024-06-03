
from src.color import color
import docker
import json

class PromoteImage:
    DOCKER = None
    PROMOTED_BRANCH = 'main'
    FINGERPRINT_LABEL = 'container.fingerprint'
    PARENT_LABEL = 'container.parent'
    current_images = None
    pulled_images = []
    promoted_images = []

    # promoting an image consists of:
    #   1. check if image has already been promoted and if so, skip remaining steps  
    #   2. determine if image exists locally, an if not pull it 
    #   3. change image tag to 'main' then push, then delete 'image:main'
    #   4. change image tag to {fingerprint} then push  then delete 'image{fingerprint}'
    #   5. if image was pulled, delete the original image

    def __init__(self, info):
        self.id = info.get('ID')
        self.repository = info.get('Repository')
        self.tag = info.get('Tag')
        self.size = info.get('Size')
        self.name = f'{self.repository}:{self.tag}'
        self.is_pulled = False

    @staticmethod
    def __get_repository(name):
        parts = name.split(':')
        parts.pop(len(parts)-1)
        return ':'.join(parts)

    def promote(self, branch):
        if self.id not in PromoteImage.promoted_images:
            if self.id not in [image.get('Id') for image in PromoteImage.current_images] and self.id not in PromoteImage.pulled_images:
                self.__pull(self.repository, tag=branch)

            print(color.change("GREY", f'docker inspect {self.name}'))
            self.info = PromoteImage.DOCKER.inspect_image(self.id)
            labels = self.info.get('Config').get('Labels')
            self.fingerprint = labels.get(PromoteImage.FINGERPRINT_LABEL)
            self.parent = labels.get(PromoteImage.PARENT_LABEL)

            self.__push(PromoteImage.PROMOTED_BRANCH)
            self.__push(self.fingerprint)

            if self.is_pulled:
                print(color.change("GREY", f'docker rmi {self.id}'))
                PromoteImage.DOCKER.remove_image(self.id)
            PromoteImage.promoted_images.append(self.id)

    def __pull(self, repository, tag):
        print(color.change("GREY", f'docker pull {repository}'))
        resp = PromoteImage.DOCKER.pull(repository, tag=tag)
        if 0 == 1:
            for line in resp:
                print(json.dumps(line, indent=2))
        PromoteImage.pulled_images.append(self.id)
        self.is_pulled = True

    def __push(self, tag):
        new_name = f'{self.repository}:{tag}'
        print(color.change("GREY", f'docker tag {self.name} {tag}'))
        PromoteImage.DOCKER.tag(self.name, self.repository, tag=tag)
        print(color.change("GREY", f'docker push {new_name}'))
        resp = PromoteImage.DOCKER.push(self.repository, tag=tag, stream=True, decode=True)
        if 0 == 1:
            for line in resp:
                print(line)
        print(color.change("GREY", f'docker rmi {new_name}'))
        PromoteImage.DOCKER.remove_image(new_name)

    def parent(self):
        # check for parent with either fingerprint or PromoteImage.DEV_BRANCH
        #  either locally or in registry
        return self.parent

    @staticmethod
    def set_globals():
        PromoteImage.DOCKER = docker.APIClient(base_url='unix://var/run/docker.sock')
        print(color.change("GREY", 'docker images'))
        PromoteImage.current_images = PromoteImage.DOCKER.images(name=None)
