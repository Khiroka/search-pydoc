import os

import requests
import slack


class SearchDocModule:
    def __init__(self, module_name):
        self.client = slack.WebClient(token=os.environ["SLACK_API_TOKEN"])
        self.module_name = module_name
        self.url = f"https://docs.python.org/ja/3/library/{self.module_name}.html"

    def check_str(self):
        return isinstance(self.module_name, str)

    def check_doc_url(self):
        response = requests.get(self.url)
        return response

    def main(self):
        if not self.check_str():
            return "NG"

        if self.check_doc_url().status_code == 200:
            return "OK"


if __name__ == "__main__":
    pass
