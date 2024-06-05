
from src.color import color
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

    def __init__(self, info, branch):
        self.id = info.get('ID')
        self.repository = info.get('Repository')
        self.tag = info.get('Tag')
        self.name = f'{self.repository}:{self.tag}'
        self.branch = branch

    @staticmethod
    def __get_repo_and_tag(name):
        parts = name.split(':')
        tag = parts.pop(len(parts)-1)
        return [ ':'.join(parts), tag ]

    def promote(self):
        if self.id in PromoteImage.promoted_images:
            return
        if self.id not in [image.get('Id') for image in PromoteImage.current_images] and self.name not in PromoteImage.pulled_images:
            self.__pull(self.repository, tag=self.branch)

        print(color.change("GREY", f'docker inspect {self.name}'))
        self.info = PromoteImage.DOCKER.inspect_image(self.id)
        labels = self.info.get('Config').get('Labels')
        self.fingerprint = labels.get(PromoteImage.FINGERPRINT_LABEL)
        self.parent = labels.get(PromoteImage.PARENT_LABEL)
        self.__push(PromoteImage.PROMOTED_BRANCH)
        self.__push(self.fingerprint)
        PromoteImage.promoted_images.append(self.name)

#            if self.is_pulled:
#                print(color.change("GREY", f'docker rmi {self.id}'))
#                PromoteImage.DOCKER.remove_image(self.id)

    def __pull(self, repository, tag):
        name = f'{repository}:{tag}'
        print(color.change("GREY", f'docker pull {name}'))
        try:
            resp = PromoteImage.DOCKER.pull(repository, tag=tag)
            if 0 == 1:
                for line in resp:
                    print(json.dumps(line, indent=2))
            PromoteImage.pulled_images.append(name)
            return name
        except Exception as e:
            print(color.change("RED", e))
        return None

    def __push(self, tag):
        name = f'{self.repository}:{tag}'
        print(color.change("GREY", f'docker tag {self.name} {name}'))
        PromoteImage.DOCKER.tag(self.name, self.repository, tag=tag)
        print(color.change("GREY", f'docker push {name}'))
        try:
            resp = PromoteImage.DOCKER.push(self.repository, tag=tag, stream=True, decode=True)
            if 0 == 1:
                for line in resp:
                    print(line)
            print(color.change("GREY", f'docker rmi {name}'))
            PromoteImage.DOCKER.remove_image(name)
            return name
        except Exception as e:
            print(color.change("RED", e))
        return None

    def get_parent(self):
        parent_repository, parent_fingerprint = self.__get_repo_and_tag(self.parent)
        # check for parent with either fingerprint or PromoteImage.DEV_BRANCH
        # either locally or in registry. If image is not local, pull from registry
        #   1. check if image exists locally
        #   2. check if {branch} tag exists locally
        #   3. check if image exists in registry
        #   4. check if {branch} tag exists in registry
        name = None
        tag = None
        for image in PromoteImage.current_images:
            if self.parent in image.get('RepoTags'): 
                name = self.parent
                tag = parent_fingerprint
                break
            dev_name = f'{parent_repository}:{self.branch}'
            if dev_name in image.get('RepoTags'): 
                name = dev_name
                tag = self.branch
                break
        if name == None:
            name = self.__pull(parent_repository, parent_fingerprint)
            tag = parent_fingerprint
        if name == None:
            name = self.__pull(parent_repository, self.branch)
            tag = self.branch
        if name == None or tag == None:
            return None
        # inspect image and verify fingerprint
        # if correct image return information
        print(color.change("GREY", f'docker inspect {name}'))
        info = PromoteImage.DOCKER.inspect_image(name)
        labels = info.get('Config').get('Labels')
        if labels == None or parent_fingerprint != labels.get(PromoteImage.FINGERPRINT_LABEL):
            return None
        return { 'ID': info.get('Id'), 'Repository': parent_repository, 'Tag': tag }

    @staticmethod
    def set_globals(client):
        PromoteImage.DOCKER = client
        print(color.change("GREY", 'docker images'))
        PromoteImage.current_images = PromoteImage.DOCKER.images(name=None)
