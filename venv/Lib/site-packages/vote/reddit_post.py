from os.path import join as joinpath, exists
from os import mkdir
import json

import requests

from .version import __version__


class RedditPost:
        base_url = "https://www.reddit.com/%s.json"
        cache_dir = 'reddit_cache'
        user_agent = 'vote ' + __version__

        def __init__(self, post_id, cache=False, cache_dir=None):
                self._post_id = post_id
                self._cache = cache
                self._cache_dir = cache_dir or self.cache_dir


        def _get_content(self):
                j = self._get_post_json()
                js = json.loads(j)
                content = js[0]['data']['children'][0]['data']['selftext']
                return content


        def _get_post_json(self):
                cached_json = self._lookup_cache()
                if cached_json is not None:
                        return cached_json

                url = self.base_url%self._post_id
                print('getting reddit post: %s'%url)

                response = requests.get(url, headers={'User-Agent' : self.user_agent})

                if response.status_code == 200:
                        self._cache_post_json(response.text)

                return response.text


        def _cache_post_json(self, j):
                if not exists(self._cache_dir):
                        mkdir(self._cache_dir)

                if self._cache:
                        filepath = joinpath(self._cache_dir, self._post_id)
                        with open(filepath, 'w') as f:
                                f.write(j)


        def _lookup_cache(self):
                if not self._cache:
                        return None

                filepath = joinpath(self._cache_dir, self._post_id)
                if not exists(filepath):
                        return None

                with open(filepath, 'r') as f:
                        return f.read()


        content = property(_get_content)