import re

from .reddit_post import RedditPost
from .image_poll import ImagePoll
from .straw_poll import StrawPollError, VotePass


class Polls:
        
        def __init__(self):
                self._map = {
                        'reddit_image_poll'     : self._reddit_image_poll
                }


        def run(self, poll_name, params=None):
                if not poll_name in self._map.keys():
                        print('no such poll')
                        print('available polls:\n' + '\n'.join(self._map.keys()))
                        return

                method = self._map[poll_name]
                method(params)


        def _reddit_image_poll(self, params):
                if not 'post_id' in params.keys():
                        print('please provide a reddit post id')
                        return

                rp = RedditPost(post_id=params['post_id'], cache=True)
                j = rp.content

                list_item_regex = re.compile("\d+\.\s+\[(.*?)\]\((.*?)\).*\((.*?)\)")
                matches = list_item_regex.findall(j)

                for m in matches:
                        ip = ImagePoll(title=m[0].strip(), image_url=m[1].strip(), poll_url=m[2].strip(), cache_images=True)
                        try:
                                success = ip.vote()
                                if not success:
                                        print('failure in casting vote')
                        except VotePass:
                                pass
                        except StrawPollError as e:
                                print(e)
                                break
