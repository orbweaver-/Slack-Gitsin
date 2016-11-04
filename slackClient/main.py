#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Libraries
from __future__ import unicode_literals
import requests
import requests.packages.urllib3

import os
import signal
import slackclient  #for real time parts
import time

from prompt_toolkit                         import prompt
from prompt_toolkit.contrib.completers      import WordCompleter
from prompt_toolkit.history                 import FileHistory
from prompt_toolkit.auto_suggest            import AutoSuggestFromHistory
from prompt_toolkit.interface               import AbortAction
from prompt_toolkit.filters                 import Always
from prompt_toolkit.interface               import AcceptAction
from prompt_toolkit.token                   import Token
from prompt_toolkit.key_binding.manager     import KeyBindingManager
from prompt_toolkit.keys                    import Keys

from sys import platform as _platform
import threading
from threading import Event, Thread

requests.packages.urllib3.disable_warnings()

# Local files
from utils import TextUtils
from completer import Completer

from realTime import rtm
from slack import Slack
from style import DocumentStyle

#Check if the settings file is correct
if os.path.isfile("settings.py"):
    import settings
else:
    raise NameError('Please create a settings.py file')


manager = KeyBindingManager.for_prompt()
windows = _platform == "win32"

# Create real time thread
t = threading.Thread(target=rtm, args=(settings.token,))
t.start()

def get_bottom_toolbar_tokens(cli):
    return [(Token.Toolbar, ' F10 : Exit ')]

@manager.registry.add_binding(Keys.F10)
def _(event):
    def exit():
        """
            Quit when the `F10` key is pressed
        """
        pid = os.getpid()
        os.kill(pid, signal.SIGTERM)  # or signal.SIGKILL
        quit()  # exit the program

    event.cli.run_in_terminal(exit)


def main():
    # Start the Slack Client
    """
    if windows:
        os.system("cls")
    else:
        os.system("clear; figlet 'Slack Gitsin' | lolcat")
    """
    history = FileHistory(os.path.expanduser("~/.slackHistory"))
    while True:
        text = prompt("slack> ", history=history,
                      auto_suggest=AutoSuggestFromHistory(),
                      on_abort=AbortAction.RETRY,
                      style=DocumentStyle,
                      completer=Completer(fuzzy_match=False,
                                          text_utils=TextUtils()),
                      complete_while_typing=Always(),
                      get_bottom_toolbar_tokens=get_bottom_toolbar_tokens,
                      key_bindings_registry=manager.registry,
                      accept_action=AcceptAction.RETURN_DOCUMENT
        )
        slack = Slack(text)
        slack.run_command()


if __name__ == '__main__':
    main()
