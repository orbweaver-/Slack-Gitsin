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

import prompt_toolkit
from prompt_toolkit.keys                    import Keys
from prompt_toolkit.history                 import FileHistory
from sys import platform as _platform
import threading
from threading import Event, Thread

requests.packages.urllib3.disable_warnings()

# Local files
from realTime import rtm
from slack import Slack
from prompt import promptUser

#Check if the settings file is correct
if os.path.isfile("settings.py"):
    import settings
else:
    raise NameError('Please create a settings.py file')



windows = _platform == "win32"

# Create real time thread
t = threading.Thread(target=rtm, args=(settings.token,))
t.start()

manager = prompt_toolkit.key_binding.manager.KeyBindingManager.for_prompt()
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
        promptUser(history)


if __name__ == '__main__':
    main()
