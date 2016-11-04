import websocket
import requests
import logging
import json
import sys
import time
logging.basicConfig()
from slack import Slack
from colorama import init, Fore, Back, Style
init()

s = Slack("foo")

def on_close(ws):
    print "### closed ###"

def on_error(ws, error):
    print error

class rtm:
    def __init__(self, token):
        url = "https://www.slack.com/api/rtm.start?token={token}".format(token=token)
        try:
            response = requests.get(url).json()
        except ValueError:
            print "\nAPI error: no response"
            return
        if response["ok"]:
            self.channels = response["channels"]
            self.ims = response["ims"]
            self.users = response["users"]
            self.ws = websocket.WebSocketApp(response["url"], on_message=self.message, on_close=on_close, on_error=on_error)
            self.ws.run_forever()

    def message(self, ws, message):
        message = json.loads(message)
        text = ""
        if "type" in message and message["type"] == "hello":
            self.socket_hello(message)
        elif "type" in message and message["type"] == "message":
            self.socket_message(message)
        elif "type" in message and message["type"] == "presence_change":
            self.socket_presence_change(message)
        elif "type" in message and (message["type"] == "user_typing"):
            self.typing(message)
        elif "type" in message and (message["type"] == "reconnect_url" or message["type"] == "channel_marked"):
            return
        else:
            print "\n" + str(message)

    def typing(self, message):
        text = Style.RESET_ALL + Style.BRIGHT + "#" + self.get_channel_name(message["channel"])
        text += Style.BRIGHT + Fore.RED + "@"
        if "user" in message:
            text += Slack.find_user_name(s, message["user"]) + ": "
        elif "username" in message:
            text += i["username"] + ": "
        text += Style.RESET_ALL + Slack.format_text(s, "is typing")
        sys.stdout.write(str((text.encode('ascii', 'ignore').decode('ascii'))))

    def socket_hello(self, message):
        text = "\nSlack messaging connected"
        sys.stdout.write(str((text.encode('ascii', 'ignore').decode('ascii'))))

    def get_channel_name(self, channel_id):
        for c in self.channels:
            if c["id"] == channel_id:
                return "#" + c["name"]
        for i in self.ims:
            if i["id"] == channel_id:
                for u in self.users:
                    if u["id"] == i["user"]:
                        channel_name = ""
                        if "first_name" in u["profile"]:
                            channel_name += u["profile"]["first_name"] + " "
                        if "last_name" in u["profile"]:
                            channel_name += u["profile"]["last_name"] + " "
                        return channel_name + "(@" + u["name"] + ")"
        return ""

    def socket_message(self, message):
        if not "text" in message:
            return
        text = Style.RESET_ALL + Fore.YELLOW + Style.DIM + "\n\n[" + time.ctime(float(message["ts"])) + "] \n"
        text += Style.BRIGHT + "Channel: " + self.get_channel_name(message["channel"]) + "\n"
        text += Style.BRIGHT + Fore.RED + "@"
        if "user" in message:
            text += Slack.find_user_name(s, message["user"]) + ": "
        elif "username" in message:
            text += i["username"] + ": "
        # Add the text
        text += Style.RESET_ALL + Slack.format_text(s, message["text"]) + '\n'
        sys.stdout.write(str((text.encode('ascii', 'ignore').decode('ascii'))))

    def socket_presence_change(self, message):
        text = Style.BRIGHT + Fore.RED + "\n@" + Slack.find_user_name(s, message["user"]) + Style.RESET_ALL + " is now " + Fore.YELLOW + message["presence"] + "\n" + Style.RESET_ALL
        sys.stdout.write(str((text.encode('ascii', 'ignore').decode('ascii'))))
