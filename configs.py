import json
import logging
import os
import platform

import eventbus

CONFIG_PATH = os.path.join(os.path.expanduser('~'), ".aosp-view.json")

KEY_GIT_PATH = 'git_path'
KEY_INIT_URL = 'init_url'
KEY_REPO_PATH = 'repo_path'


class Configs:
    _instance = None

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        if self._instance is None:
            self.configs = {}

    def set_default(self):
        logging.debug(f"set default configs")
        if not self.configs.get(KEY_GIT_PATH):
            self.configs[KEY_GIT_PATH] = self.default_git()

    def read(self):
        if os.path.isfile(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                self.configs = json.load(f)

    def write(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.configs, f, indent=2)
        logging.debug(f"update config {self.configs}")
        logging.debug(f"update config {CONFIG_PATH}")
        eventbus.emit(eventbus.TOPIC_LOG, f"update config {CONFIG_PATH}")

    def get(self, key, default_value=None):
        return self.configs.get(key, default_value)

    @staticmethod
    def default_git():
        cmd = 'which git'
        if platform.system() == 'Windows':
            cmd = 'where git'
        result = os.popen(cmd)
        paths = result.read()
        path = paths.strip('\r\n').split('\n')[0]
        if os.path.isfile(path):
            logging.debug(f"find git {path}")
            eventbus.emit(eventbus.TOPIC_LOG, f"find git {path}")
            return path
        logging.debug(f"git not found: {path}")
        return ''

    def update(self, c: dict):
        self.configs.update(c)


_configs = Configs()


def init():
    _configs.read()
    _configs.set_default()


def write():
    Configs().write()


def update(c):
    Configs().update(c)


def init_url():
    return _configs.get(KEY_INIT_URL, '')


def repo_path():
    return _configs.get(KEY_REPO_PATH, '')


def git_path():
    return _configs.get(KEY_GIT_PATH, '')
