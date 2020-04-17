import json
import os

CONFIG_PY_PATH = os.path.dirname(os.path.realpath(__file__))
CONFIG = CONFIG_PY_PATH + "/../../configs/config.json"
SECRETS = CONFIG_PY_PATH + "/../../configs/secrets.json"


class Secrets:
    def __init__(self):
        with open(SECRETS, "r", encoding="utf-8") as file:
            self.res = json.loads(file.read())

    def __getitem__(self, item):
        return self.res[item]


class Config:
    def __init__(self):
        with open(CONFIG, "r", encoding="utf-8") as file:
            self.res = json.loads(file.read())

    def __getitem__(self, item):
        return self.res[item]


# if __name__ == '__main__':
#     print(Secrets()["django_secret_key"])
