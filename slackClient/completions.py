#!/usr/bin/env python
# -*- coding: utf-8 -*-

import settings
import requests
import json

# create slack channels list
channels = {}
non_member_channels = {}
try:
    # get user_id
    url = "https://www.slack.com/api/auth.test?token={token}".format(token=settings.token)
    response = requests.get(url).json()
    user_id = response["user_id"]
except KeyError:
    raise NameError("Oath token is invalid")


# get channels that our user already member to show him
url = "https://www.slack.com/api/channels.list?token={token}".format(token=settings.token)
response = requests.get(url).json()
for i in response["channels"]:
    if i["is_member"]:
        channels.update(
            {
                i["name"]: i["purpose"]["value"]
            }
        )
    else:
        non_member_channels.update(
            {
                i["name"]: i["purpose"]["value"]
            }
        )

# get user list
users = {}
url = "https://www.slack.com/api/users.list?token={token}".format(token=settings.token)
members = requests.get(url).json()["members"]
for i in members:
    users.update(
        {
            "@" + i["name"] : i["id"]
        }
    )

coms = []
for c in channels.keys():
    coms.append("#" + c)

coms.append('list')

url = "https://www.slack.com/api/im.list?token={token}".format(token=settings.token)
response = requests.get(url).json()
if response["ok"]:
    json.dump(response, open("ims.json", "w+"))
    for i in response["ims"]:
        for u in members:
            if u["id"] == i["user"]:
                coms.append("@" + u["name"])
                break

SUBCOMMANDS = {
	"channels.history"  : "Fetches history of messages and events from a channel.",
	"channels.join"  	: "Joins a channel",
	"channels.list"  	: "Lists all channels in a Slack team.",
	"chat.postMessage"  : "Sends a message to a channel.",
	"files.upload"  	: "Upload an image/file",
	"channels.invite" 	: "Invites a user to a channels.",
	"channels.create" 	: "Creates a channels. ",
	"users.info"  	    : "Gets information about a user.",
	"users.list"        : "Lists all users in a Slack team."
}

ARGS_OPTS_LOOKUP = {
    'channels.history': {
        'args': 'Show',
        'opts': list(channels.keys()),
    },
    'channels.join': {
        'args': '"Join"',
        'opts': list(non_member_channels.keys()),
    },
    'chat.postMessage': {
        'args': '"Send"',
        'opts': list(channels.keys()),
    },
    'channels.invite': {
        'args': '"invite"',
        'opts': list(channels.keys()),
    },

    'users.info': {
        'args': 'Show',
        'opts': list(users.keys()),
    },
        'files.upload': {
        'args': 'Upload',
        'opts': list(channels.keys()),
    }

}

META_LOOKUP = {
    '10': 'limit: int (opt) limits the posts displayed',
}
META_LOOKUP.update(SUBCOMMANDS)
