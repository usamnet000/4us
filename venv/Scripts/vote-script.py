#!C:\Users\a\PycharmProjects\4us3\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'vote==1.0.2','console_scripts','vote'
__requires__ = 'vote==1.0.2'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('vote==1.0.2', 'console_scripts', 'vote')()
    )
