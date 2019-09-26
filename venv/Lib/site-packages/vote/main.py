
from redcmd.api import maincmd, execute_commandline

from .polls import Polls


@maincmd
def cli(poll_name, id=None):

        params = {}
        params['post_id'] = id

        polls = Polls()
        polls.run(poll_name, params=params)


def main():
        execute_commandline()
