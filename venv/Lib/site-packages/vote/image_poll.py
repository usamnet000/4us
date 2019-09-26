from os.path import join as joinpath, exists
from os import mkdir

import requests
from redlib.api.system import sys_command

from .straw_poll import StrawPoll


class ImagePoll:
        cache_folder = 'image_cache'


        def __init__(self, title, image_url, poll_url, cache_images=True, cache_folder=None):
                self._title     = title
                self._image_url = image_url
                self._poll_url  = poll_url

                self._cache_images = cache_images
                self._cache_folder = cache_folder or self.cache_folder

                self._strawpoll = StrawPoll()


        def vote(self):
                print(self._title)
                poll_id = self._poll_url.split('/')[-1]

                if self._strawpoll.already_voted(poll_id):
                        print('already voted')
                        return True
                        
                filepath = self._download_image()
                self._show_image(filepath)

                return self._strawpoll.vote(poll_id)


        def _show_image(self, filepath):
                sys_command("cmd /c start %s"%filepath)
                

        def _download_image(self):
                filename = self._image_url.split('/')[-1]
                filepath = self._lookup_cache(filename)
                if filepath is not None:
                        return filepath

                print('getting image: %s'%self._image_url)
                response = requests.get(self._image_url)

                if not self._cache_images:
                        return self._save_image(response.content, filename)
                else:
                        return self._cache_image(response.content, filename)


        def _save_image(self, data, filename):
                with open(filename, 'wb') as f:
                        f.write(data)

                return filename


        def _cache_image(self, data, filename):
                if not exists(self._cache_folder):
                        mkdir(self._cache_folder)

                filepath = joinpath(self.cache_folder, filename)

                with open(filepath, 'wb') as f:
                        f.write(data)

                return filepath


        def _lookup_cache(self, filename):
                filepath = joinpath(self.cache_folder, filename)
                if exists(filepath):
                        return filepath
                else:
                        return None