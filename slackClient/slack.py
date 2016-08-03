#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import click
import requests
import settings
import os
import subprocess
import time
import slackclient  # for real time parts
import re
import json
import sys

from prettytable import PrettyTable
from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter

from completions import users
from style import DocumentStyle
from settings import lolcat
from sys import platform as _platform
windows = _platform == "win32"

lString = ""

if os.path.isfile("channels.json"):
    channels = json.load(open("channels.json", "r"))
else:
    json.dump({}, open("channels.json", "w+"))
    channels = {}

if os.path.isfile("users.json"):
    users = json.load(open("users.json", "r"))
else:
    json.dump({}, open("users.json", "w+"))
    users = {}

from colorama import init, Fore, Back, Style
init()

if lolcat:
    lString = " | lolcat"

class Slack(object):
    def __init__(self, text):
        self.text = text

    def get_channels_list(self):
        # create slack channels list
        channels = []
        url = "https://www.slack.com/api/channels.list?token={token}".format(token=settings.token)
        response = requests.get(url).json()
        return response["channels"]

    def channels_join(self, name):
        url = "https://www.slack.com/api/channels.join?token={token}&name={name}".format(token=settings.token,
                                                                                     name=name)
        response = requests.get(url).json()
        if response["ok"]:
            os.system("figlet 'Joined'" + lString)
            time.sleep(2)
            os.system("clear")
        else:
            print "something goes wrong :( (\u001b[1m\u001b[31m " + response["error"] + "\u001b[0m)"

    def channels_history(self, channel_name):
        # Retrieve channel id by using channel_name
        channel_id = self.find_channel_id(channel_name)
        url = "https://www.slack.com/api/channels.info?token={token}&channel={channel_id}".format(token=settings.token,channel_id=channel_id)
        response = requests.get(url).json()
        if response['ok']:
            if os.path.isfile("messages/" + channel_id + ".json") and response["channel"]["unread_count"] == 0 :
                res = json.load(open("messages/" + channel_id + ".json", "r"))
                self.print_history(res, channel_name)
            else:
                url = "https://www.slack.com/api/channels.history?token={token}&channel={channel_id}".format(token=settings.token,channel_id=channel_id)
                response = requests.get(url).json()
                if response['ok']:
                    json.dump(response, open("messages/" + channel_id + ".json", "w+"))
                    self.print_history(response, channel_name)
                else:
                    print "something goes wrong!"
        else:
            print "something goes wrong!"


    def post_message(self, channel_name):
        # self.channels_history(channel_name)
        os.system("echo '\u001b[1m\u001b[31m  To mention a user write @ while chatting \u001b[0m'")
        text = prompt("your message > ", completer=WordCompleter(users))
        channel_id = self.find_channel_id(channel_name)
        url = "https://www.slack.com/api/chat.postMessage?token={token}&channel={channel_id}&text={text}&as_user=true&link_names=1".format(
            token=settings.token,
            text=text,
            channel_id=channel_id)
        response = requests.get(url).json()
        # TODO : retrieve message history and print to screen while chatting
        if response["ok"]:
            os.system("figlet 'Sent'" + lString)
            time.sleep(2)
            os.system("clear")
        else:
            print "something goes wrong :( (\u001b[1m\u001b[31m " + response["error"] + "\u001b[0m)"

    def channels_invite(self, channel_name):
        channel_id = self.find_channel_id(channel_name)
        invites = prompt("send invites -> ", completer=WordCompleter(users),
                         style=DocumentStyle)
        for i in invites.split(" "):
            user_id = self.find_user_id(i.strip("@"))
            url = "https://www.slack.com/api/channels.invite?token={token}&channel={channel_id}&user={user}".format(
                token=settings.token,
                channel_id=channel_id,
                user=user_id)
            response = requests.get(url).json()
            if response["ok"]:
                os.system("figlet 'Invited " + i + lString)
                time.sleep(2)
                os.system("clear")
            else:
                print "something goes wrong :( (\u001b[1m\u001b[31m " + response["error"] + "\u001b[0m)"

    def channels_create(self):
        os.system("clear")
        fields = ["name", "purpose(OPTINAL)", "send invite"]
        for i in fields:
            if i == "name":
                name = raw_input("\u001b[1m\u001b[31m channel name -> \u001b[0m")
            elif i == "purpose(OPTINAL)":
                purpose = raw_input("\u001b[1m\u001b[31m purpose of the channel(OPTINAL) : \u001b[0m")
            else:
                invites = prompt("send invites -> ", completer=WordCompleter(users),
                                 style=DocumentStyle)

        url = "https://www.slack.com/api/channels.create?token={token}&name={name}&purpose={purpose}".format(
            token=settings.token,
            name=name,
            purpose=purpose)
        response = requests.get(url).json()
        # TODO :  send channel and user_id to channels_invite
        if response["ok"]:
            os.system("figlet 'Created'" + lString)
            time.sleep(2)
            os.system("clear")

    def users_list(self):
        # get user list
        os.system("clear")
        users = {};
        url = "https://www.slack.com/api/users.list?token={token}".format(token=settings.token)
        response = requests.get(url).json()
        text = PrettyTable(["name", "tz", "tz_label", "email"])
        for i in response["members"]:
            text.add_row([i["name"], str(i["tz"]), str(i["tz_label"]), str(i["profile"]["email"])])

        # os.system("echo '" + text + "' | lolcat")
        print text

    def users_info(self, user_name):
        user_id = self.find_user_id(user_name.strip("@"))
        url = "https://www.slack.com/api/users.info?token={token}&user={user_id}".format(token=settings.token,
                                                                                     user_id=user_id)
        response = requests.get(url).json()
        if response["ok"]:
            self.print_users_info(response['user'])
        else:
            print "something goes wrong :( (\u001b[1m\u001b[31m " + response["error"] + "\u001b[0m)"

    def file_upload(self, channel_name):
        os.system("clear")
        channel_id = self.find_channel_id(channel_name)
        fields = ["file", "content", "filename", "title", "initial_comment"]
        for i in fields:
            if i == "file":
                os.system("echo 'opening the file dialog. wait...' ")
                file = subprocess.check_output(['zenity', '--file-selection'])
                os.system("echo '\u001b[1m\u001b[31m file : \u001b[0m'" + file + "'")
            elif i == "content":
                content = raw_input("\u001b[1m\u001b[31m content : \u001b[0m")
            elif i == "filename":
                filename = raw_input("\u001b[1m\u001b[31m filename : \u001b[0m")
            elif i == "title":
                title = raw_input("\u001b[1m\u001b[31m title : \u001b[0m")
            else:
                initial_comment = prompt("add comment : ", completer=WordCompleter(users),
                                         style=DocumentStyle)
        url = "https://www.slack.com/api/files.upload?token={token}&content={content}&filename={filename}&channels={channel_id}&title={title}&initial_comment={initial_comment}".format(
            token=settings.token,
            content=content,
            filename=filename,
            channel_id=channel_id,
            title=title,
            initial_comment=initial_comment)
        response = requests.get(url).json()
        if response["ok"]:
            os.system("figlet 'Uploaded!'" + lString)
            time.sleep(2)
            os.system("clear")
        else:
            print "something goes wrong :( (\u001b[1m\u001b[31m " + response["error"] + "\u001b[0m)"

    def find_channel_id(self, channel_name):
        if channel_name in channels:
            return channels[channel_name]
        url = "https://www.slack.com/api/channels.list?token={token}".format(token=settings.token)
        response = requests.get(url).json()
        for i in response["channels"]:
            if i["name"] == channel_name:
                channels[channel_name] = i["id"]
                json.dump(channels, open("channels.json", "w+"))
                return i["id"]
        return None

    def find_user_id(self, user_name):
        url = "https://www.slack.com/api/users.list?token={token}".format(token=settings.token)
        response = requests.get(url).json()
        for i in response["members"]:
            if i["name"] == user_name:
                return i["id"]
        return None

    def find_user_name(self, user_id):
        if user_id in users:
            return users[user_id]
        url = "https://www.slack.com/api/users.list?token={token}".format(token=settings.token)
        response = requests.get(url).json()
        for i in response["members"]:
            if i["id"] == user_id:
                users[user_id] = i["name"]
                json.dump(users, open("users.json", "w+"))
                return i["name"]
        return None

    def print_history(self, response, channel_name):
        if windows:
            os.system("cls;"+ lString)
        else:
            os.system("clear; figlet '" + channel_name + "'" + lString)

        response["messages"].reverse()
        for i in response["messages"]:
            # add time
            text = Style.RESET_ALL + Fore.YELLOW + Style.DIM + "[" + time.ctime(float(i["ts"])) + "] \n"

            if "upload" in i and "file" in i and i["upload"] == True:
                content = Fore.RED + Style.BRIGHT
                if "pretty_type" in i["file"]:
                    content += i["file"]["pretty_type"] + " "
                content += "UPLOAD: by @" + self.find_user_name(i["file"]["user"]) + "\n"
                if "url_private" in i["file"]:
                    content += Style.RESET_ALL + Back.WHITE + Fore.BLUE + i["file"]["url_private"] + Style.RESET_ALL
                if "initial_comment" in i["file"]:
                    content += Fore.RED + Style.BRIGHT + "\n@" + self.find_user_name(i["file"]["initial_comment"]["user"]) + ": "
                    content += Style.RESET_ALL + self.format_text(i["file"]["initial_comment"]["comment"])
                text += Style.RESET_ALL + content + '\n\n'
            else:
                # Get username
                text += Style.BRIGHT + "@"
                if "user" in i:
                    text += self.find_user_name(i["user"]) + ": "
                elif "username" in i:
                    text += i["username"] + ": "

                # Add the text
                text += Style.RESET_ALL + self.format_text(i["text"]) + '\n\n'

            sys.stdout.write(str((text.encode('ascii', 'ignore').decode('ascii'))))

    def format_text(self, text):
        # replace username_id with username
        while re.search('<@.........>', text):
            orig = re.search('<@.........>', text).group(0)
            at = Fore.RED + Style.BRIGHT + "@" + self.find_user_name(orig[2:-1]) + Style.RESET_ALL
            text = re.sub(orig, at, text, 1)

        # replace given usernames\code with username
        while re.search('<@.........\|\S*>', text):
            orig = re.search('\|\S*>', text).group(0)
            at = Fore.RED + Style.BRIGHT + "@" + orig[1:-1] + Style.RESET_ALL
            text = re.sub('<@.........\|\S*>', at, text, 1)

        # format URLs
        while re.search('<https*:\/\/.*>', text):
            orig = re.search('<https*:\/\/.*>', text).group(0)
            formatted = Back.WHITE + Fore.BLUE + orig[1:-1] + Style.RESET_ALL
            text = re.sub('<https*:\/\/.*>', formatted, text, 1)

        # format long code
        while re.search('```.*```', text, re.DOTALL):
            orig = re.search('```.*```', text, re.DOTALL).group(0)
            formatted = Back.WHITE + Fore.BLACK + orig[3:-3] + Style.RESET_ALL
            text = re.sub('```.*```', formatted, text, 1, re.DOTALL)
        return text

    def print_channels_list(self, response):
        os.system("clear; figlet '" + "All Channels" + "'" + lString)
        text = ""
        for i in response:
            text += i["name"] + "\t\t" + "(created {when})\n".format(when=time.ctime(float(i["created"])))
        # print and reset text
        os.system("echo ' " + text + "' | lolcat")

    def print_users_info(self, response):
        os.system("clear; figlet '" + "User Info" + "'" + lString)
        text = "name : " + response["name"] + "\n"
        for (key, value) in response["profile"].items():
            if type(value) == "str":
                text += key + " - > " + value + "\n"
            else:
                text += key + " - > " + str(value) + "\n"
        os.system("echo '" + text + "'" + lString)

    def run_command(self):
        try:
            split_text = self.text.split(" ")
            if split_text[1] == "channels.list":
                response = self.get_channels_list()
                self.print_channels_list(response)
            elif split_text[1] == "channels.join":
                if len(split_text) < 4:
                    print "Please enter values properly"
                else:
                    self.channels_join(split_text[3])
            elif split_text[1] == "channels.history":
                if len(split_text) < 4:
                    print "Please enter values properly!"
                else:
                    self.channels_history(split_text[3])  # send channel_name
            elif split_text[1] == "chat.postMessage":
                self.post_message(split_text[3])
            elif split_text[1] == "channels.invite":
                self.channels_invite(split_text[3])  # send channel_name
            elif split_text[1] == "channels.create":
                self.channels_create()
            elif split_text[1] == "users.list":
                self.users_list()
            elif split_text[1] == "users.info":
                self.users_info(split_text[3])
            elif split_text[1] == "files.upload":
                self.file_upload(split_text[3])
        except:
            print "something goes wrong!"
