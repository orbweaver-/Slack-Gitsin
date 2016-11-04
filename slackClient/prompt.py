#!/usr/bin/env python
# -*- coding: utf-8 -*-

import prompt_toolkit
from style import DocumentStyle
from completer import Completer
from utils import TextUtils
manager = prompt_toolkit.key_binding.manager.KeyBindingManager.for_prompt()
always = prompt_toolkit.filters.Always()
def get_bottom_toolbar_tokens(cli):
    return [(prompt_toolkit.token.Token.Toolbar, ' F10 : Exits')]

def promptUser(history):
    text = prompt_toolkit.prompt("slack> ",
                history                     = history,
                auto_suggest                = prompt_toolkit.auto_suggest.AutoSuggestFromHistory(),
                on_abort                    = prompt_toolkit.interface.AbortAction.RETRY,
                style                       = DocumentStyle,
                completer                   = Completer(fuzzy_match=False,
                                                text_utils=TextUtils()),
                complete_while_typing       = always,
                get_bottom_toolbar_tokens   = get_bottom_toolbar_tokens,
                key_bindings_registry       = manager.registry,
                accept_action               = prompt_toolkit.interface.AcceptAction.RETURN_DOCUMENT
    )
    slack = Slack(text)
    slack.run_command()
