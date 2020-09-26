import os

from flask import Flask
import requests
import slack

app = Flask(__name__)


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


@app.route("/search-doc")
def main(request):
    sdm = SearchDocModule(request)

    if not sdm.check_str():
        return "NG"

    if sdm.check_doc_url().status_code == 200:
        return "OK"
    else:
        return "NG"


if __name__ == "__main__":
    app.run(debug=True)
