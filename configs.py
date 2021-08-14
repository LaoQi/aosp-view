import json
import logging
import os

import eventbus

CONFIG_PATH = os.path.join(os.path.expanduser('~'), ".aosp-view.json")


class Configs:
    def __init__(self):
        self.configs = {}
        self.read()

    def read(self):
        if os.path.isfile(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                self.configs = json.load(f)

    def write(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.configs, f, indent=2)
        eventbus.emit(eventbus.TOPIC_LOG, f"update config {CONFIG_PATH}")

    def update(self, c: dict):
        self.configs.update(c)

    @property
    def init_url(self):
        return self.configs.get('init_url', '')

    @property
    def repo_path(self):
        return self.configs.get('repo_path', '')

    @property
    def git_path(self):
        return self.configs.get('git_path', '')


_configs = Configs()


def read():
    _configs.read()


def write():
    _configs.write()


def update(c):
    _configs.update(c)


def get():
    return _configs
