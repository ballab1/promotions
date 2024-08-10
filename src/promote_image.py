
from src.color import color
import docker.errors as derrors
import json

class PromoteImage:
    DOCKER = None
    PROMOTED_BRANCH = 'main'
    FINGERPRINT_LABEL = 'container.fingerprint'
    PARENT_LABEL = 'container.parent'
    current_images = None
    promoted_images = []
    images_to_remove = []

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
        print(color.change("cyan", f'\n  Promoting {self.name}'))
        if self.id not in [image.get('Id') for image in PromoteImage.current_images]:
            self.__pull(self.repository, tag=self.branch)

        # print(color.change("GREY", f'    docker inspect {self.name}'))
        self.info = PromoteImage.DOCKER.inspect_image(self.id)
        labels = self.info.get('Config').get('Labels')
        self.fingerprint = labels.get(PromoteImage.FINGERPRINT_LABEL)
        self.parent = labels.get(PromoteImage.PARENT_LABEL)
        self.__push(self.fingerprint)
        self.__push(PromoteImage.PROMOTED_BRANCH)

    def __pull(self, repository, tag, ignore_not_found=False):
        name = f'{repository}:{tag}'
        for image in PromoteImage.current_images:
            if name in image.get('RepoTags'):
                return name
        print(color.change("GREY", f'    docker pull {name}'))
        try:
            response = PromoteImage.DOCKER.pull(repository, tag=tag, stream=True, decode=True)
            for obj in response:
                status = obj.get('status')
                if status in (None, 'Already exists'):
                    continue
                idd = obj.get('id')
                if idd:
                    print(color.change("GREY", f'      {idd}: {status}'))
                elif status != f'{tag} from {repository}':
                    print(color.change("GREY", f'      {status}'))
            info = PromoteImage.DOCKER.inspect_image(name)
            image = { 'ID': info.get('ID'),
                      'Repository': repository,
                      'Tag': tag,
                      'RepoTags': info.get('RepoTags') }
            PromoteImage.current_images.append(image)
            PromoteImage.images_to_remove.append(name)
            return name
        except derrors.NotFound as e:
            if ignore_not_found:
                print(color.change("GREY", f'      Image {name} not found'))
            else:
                print(color.change("RED", e.explanation))
        except Exception as e:
            print(color.change("RED", e))
        return None

    def __push(self, tag):
        name = f'{self.repository}:{tag}'
        print(color.change("GREY", f'    docker tag {self.name} {name}'))
        PromoteImage.DOCKER.tag(self.name, self.repository, tag=tag)
        print(color.change("GREY", f'    docker push {name}'))
        try:
            response = PromoteImage.DOCKER.push(self.repository, tag=tag, stream=True, decode=True)
            for obj in response:
                status  =  obj.get('status')
                if status not in (None, 'Preparing', 'Waiting', 'Layer already exists'):
                    print(color.change("GREY", f'      {status}'))
            PromoteImage.images_to_remove.append(name)
            return name
        except Exception as e:
            print(color.change("RED", e))
        return None

    def get_parent(self):
        parent_repository, parent_fingerprint = self.__get_repo_and_tag(self.parent)
        # check for parent with either fingerprint or PromoteImage.DEV_BRANCH
        # either locally or in registry. If image is not local, pull from registry
        #   1. check if image exists locally
        #   2. check if {fingerprint} tag exists locally
        #   3. check if image exists in registry
        #   4. check if {branch} tag exists in registry
        name = None
        tag = None
        for image in PromoteImage.current_images:
            repo_tags = image.get('RepoTags')
            if self.parent in repo_tags: 
                name = self.parent
                tag = parent_fingerprint
                break
            dev_name = f'{parent_repository}:{self.branch}'
            if dev_name in repo_tags: 
                name = dev_name
                tag = self.branch
                break
        if name == None:
            name = self.__pull(parent_repository, parent_fingerprint, True)
            tag = parent_fingerprint
        if name == None:
            name = self.__pull(parent_repository, self.branch)
            tag = self.branch
        if name == None or tag == None:
            return None
        # inspect image and verify fingerprint: if correct image return information
        info = PromoteImage.DOCKER.inspect_image(name)
        labels = info.get('Config').get('Labels')
        if labels == None or parent_fingerprint != labels.get(PromoteImage.FINGERPRINT_LABEL):
            return None
        return { 'ID': info.get('Id'),
                 'Repository': parent_repository,
                 'Tag': tag,
                 'RepoTags': info.get('RepoTags')
            }

    @staticmethod
    def remove_images(primary_images):
        print(color.change("BLUE", '\n  Removing unneeded images'))
        removed = []
        for name in sorted(PromoteImage.images_to_remove):
            if name in removed or name in primary_images:
                continue
            removed.append(name)
            print(color.change("GREY", f'    docker rmi {name}'))
            PromoteImage.DOCKER.remove_image(name)

    @staticmethod
    def set_globals(client):
        PromoteImage.DOCKER = client
        print(color.change("GREY", '  docker images'))
        PromoteImage.current_images = PromoteImage.DOCKER.images(name=None)
