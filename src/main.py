import os
import re
from pprint import pprint

from flask import Flask
import requests
from slack import WebClient
from slackeventsapi import SlackEventAdapter

app = Flask(__name__)
slack_signing_secret = os.environ["SIGINING"]
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events", app)

slack_bot_token = os.environ["PYDOC_TOKEN"]
slack_client = WebClient(slack_bot_token)

functions = {
    "abs": "abs",
    "delattr": "delattr",
    "hash": "hash",
    "memoryview": "func-memoryview",
    "set": "func-set",
    "all": "all",
    "dict": "func-dict",
    "help": "help",
    "min": "min",
    "setattr": "setattr",
    "any": "any",
    "dir": "dir",
    "hex": "hex",
    "next": "next",
    "slice": "slice",
    "ascii": "ascii",
    "divmod": "divmod",
    "id": "id",
    "object": "object",
    "sorted": "sorted",
    "bin": "bin",
    "enumerate": "enumerate",
    "input": "input",
    "oct": "oct",
    "staticmethod": "staticmethod",
    "bool": "bool",
    "eval": "eval",
    "int": "int",
    "open": "open",
    "str": "func-str",
    "breakpoint": "breakpoint",
    "exec": "exec",
    "isinstance": "isinstance",
    "ord": "ord",
    "sum": "sum",
    "bytearray": "bytearray",
    "filter": "filter",
    "issubclass": "issubclass",
    "pow": "pow",
    "super": "super",
    "bytes": "bytes",
    "float": "float",
    "iter": "iter",
    "print": "print",
    "tuple": "func-tuple",
    "callable": "callable",
    "format": "format",
    "len": "len",
    "property": "property",
    "type": "type",
    "chr": "chr",
    "frozenset": "func-frozenset",
    "list": "func-list",
    "range": "func-range",
    "vars": "vars",
    "classmethod": "classmethod",
    "getattr": "getattr",
    "locals": "locals",
    "repr": "repr",
    "zip": "zip",
    "compile": "compile",
    "globals": "globals",
    "map": "map",
    "reversed": "reversed",
    "__import__": "__import__",
    "complex": "complex",
    "hasattr": "hasattr",
    "max": "max",
    "round": "round",
}


class SearchDocModule:
    def __init__(self, module_name):
        self.module_name = module_name
        self.url = f"https://docs.python.org/ja/3/library/{self.module_name}.html"

    def check_str(self):
        return isinstance(self.module_name, str)

    def check_doc_url(self):
        response = requests.get(self.url)
        return response


@slack_events_adapter.on("message")
def main(event_data):
    message = event_data["event"]
    channel = message["channel"]
    # pprint(message)
    if message.get("subtype") is None and re.match(r"^py\s", message.get("text")):
        text = message.get("text").split()[1]
        pprint(text)
        sdm = SearchDocModule(text)

        status_code = sdm.check_doc_url().status_code
        if status_code == 200:
            print("success", status_code)
            slack_client.chat_postMessage(channel=channel, text=sdm.url)
        else:
            if text in functions:
                slack_client.chat_postMessage(
                    channel=channel,
                    text=f"https://docs.python.org/ja/3/library/functions.html#{functions[text]}",
                )
            else:
                print("not match module")
                slack_client.chat_postMessage(
                    channel=channel, text="The module name is incorrect"
                )
    # else:
    #     print("not match")
    #     slack_client.chat_postMessage(
    #         channel=channel, text="Command is [py space modulename]"
    #     )
    # ここ使うとbotが投稿した内容に反応して延々とぐるぐるするので要検討


if __name__ == "__main__":
    app.run(debug=True, port=5000)
