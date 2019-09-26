from collections import namedtuple
import pickle
import sys
from os.path import exists
from http.cookiejar import LWPCookieJar
from copy import copy
import json

import requests

from greencache.simple_cache import SimpleCache
from htmq.html_query import htmq

g_debug = True

Option = namedtuple('Option', ['title', 'value'])
def dbg_print(s):
        global g_debug
        if g_debug: print(s)


class VotePass(Exception):
        pass


class StrawPollError(Exception):
        pass


class StrawPoll:
        cookies_filename = 'strawpoll_cookies'
        poll_page_base_url = "http://strawpoll.me/"
        voted_list_filename = 'strawpoll_voted'


        def __init__(self, debug=False):
                global g_debug
                g_debug = debug

                self._session = None
                self._cookies = None
                self._load_voted_store()


        def _load_voted_store(self):
                self._store = SimpleCache(filepath=self.voted_list_filename)


        def _store_voted(self, poll_id):
                self._store.set(poll_id, True)


        def already_voted(self, poll_id):
                return self._store.get(poll_id)


        def _request(self, url, params=None, headers={}):
                if self._session is None:
                        self._session = requests.Session()
                        self._session.cookies = LWPCookieJar(self.cookies_filename)
                        if exists(self.cookies_filename):
                                self._session.cookies.load()

                headers['User-Agent']   =  "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
                headers['X-Requested-With'] = 'XMLHttpRequest'

                response = None
                if params is None:
                        response = self._session.get(url, headers=headers)
                else:
                        response = self._session.post(url, data=params, headers=headers)

                self._session.cookies.save()

                return response


        def vote(self, poll_id):
                if self.already_voted(poll_id):
                        print('already voted on this poll (%s%s)'%(self.poll_page_base_url, poll_id))
                        return

                poll_page = self._get_page(poll_id)
                options, sec_params = self._extract_info(poll_page)
                self._print_options(options)

                vote = None
                try:
                        vote = self._input_vote()
                except VotePass:
                        return True

                success = self._post_vote(poll_id, vote, options, sec_params)

                if success:
                        self._store_voted(poll_id)
                
                return success


        def _get_page(self, poll_id):
                url = self.poll_page_base_url + poll_id
                print('getting poll page: %s'%url)
                response = self._request(url)
                return response.text
                

        def _extract_info(self, page_html):                
                option_titles = htmq(page_html).all().div(id='field-options').all().div().all().span().text().q()
                option_values = htmq(page_html).all().div(id='field-options').all().div().input().attr('value').q()

                options = []
                for t, v in zip(option_titles, option_values):
                        dbg_print('%s %s'%(t, v))
                        options.append(Option(t, v))

                st = htmq(page_html).all().input(id='field-security-token').attr('value').one().q()
                nv = htmq(page_html).all().input(id='field-authenticity-token').attrs('name, value').one().q()

                sec_params = {}
                sec_params['security-token'] = st

                if nv is not None:
                        sec_params[nv[0]] = nv[1]

                dbg_print(sec_params)
                return options, sec_params


        def _print_options(self, options):
                for (i, o) in enumerate(options):
                        print('%-25s [%d]'%(o.title, i))


        def _input_vote(self):
                choice = input('enter your vote (x to exit, p to pass): ')
                if choice.lower() == 'p':
                        raise VotePass()
                elif choice.lower() == 'x':
                        raise StrawPollError('user exited the poll')
                else:
                        return int(choice)


        def _post_vote(self, poll_id, vote, options, sec_params):
                params = copy(sec_params)
                params['options'] = options[vote].value

                headers = {}
                headers['Referer'] = "http://strawpoll.me/" + poll_id
                
                url = self.poll_page_base_url + poll_id

                response = self._request(url, params=params, headers=headers)

                j = json.loads(response.text)
                return j['success'] == 'success'


if __name__ == '__main__':
        sp = StrawPoll(debug=True)
        if sp.vote(sys.argv[1]):
                print('success')
