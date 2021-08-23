import json
import logging
import os
import platform
import subprocess
from collections import OrderedDict

import eventbus
from manifest import Manifest

CONFIG_PATH = os.path.join(os.path.expanduser('~'), ".aosp-view.json")

KEY_GIT_PATH = 'git_path'
KEY_INIT_URL = 'init_url'
KEY_REPO_PATH = 'repo_path'
KEY_REF_HASH = 'ref_hash'


class Configs:

    def __init__(self):
        self.configs = {}
        self.refs = None
        self.manifest = Manifest()
        self.listen()

    def listen(self):
        eventbus.listen(eventbus.TOPIC_UPDATE_INIT_URL, lambda x: self.update({KEY_INIT_URL: x}))
        eventbus.listen(eventbus.TOPIC_UPDATE_GIT_PATH, lambda x: self.update({KEY_GIT_PATH: x}))
        eventbus.listen(eventbus.TOPIC_UPDATE_REPO_PATH, lambda x: self.update({KEY_REPO_PATH: x}))
        eventbus.listen(eventbus.TOPIC_UPDATE_MANIFEST, lambda x: self.update_manifest(x))
        eventbus.listen(eventbus.TOPIC_CHECKOUT_MANIFEST_COMPLETE, lambda x: self.update({KEY_REF_HASH: x}))

        eventbus.listen(eventbus.TOPIC_GUI_COMPLETE, lambda x: self.check_refs())

    def update_manifest(self, content):
        self.manifest.set_content(content)
        eventbus.emit(eventbus.TOPIC_UPDATE_MANIFEST_COMPLETE)

    def check_refs(self):
        logging.debug("check refs")
        if os.path.exists(os.path.join(self.get(KEY_REPO_PATH, ''), 'manifest')):
            # result = subprocess.check_output([self.get(KEY_GIT_PATH, ''), 'symbolic-ref', '--short', '-q', 'HEAD'],
            #                                  cwd=os.path.join(self.get(KEY_REPO_PATH, ''), 'manifest'))
            # self.current_ref = result.decode().strip()
            # logging.debug(f"find current ref {self.current_ref}")
            # eventbus.emit(eventbus.TOPIC_UPDATE_CURRENT_REF, self.current_ref)

            # result = subprocess.check_output([self.get(KEY_GIT_PATH, ''), 'tag', '-l'],
            #                                  cwd=os.path.join(self.get(KEY_REPO_PATH, ''), 'manifest'))
            result = subprocess.check_output(
                [
                    self.get(KEY_GIT_PATH, ''),
                    'for-each-ref',
                    '--format=%(objectname:short) %(creatordate:short) %(refname:short)',
                    '--sort=creatordate'
                ],
                cwd=os.path.join(self.get(KEY_REPO_PATH, ''), 'manifest'))
            lines = result.decode().strip().split('\n')
            logging.debug(f"find ref {len(lines)}")
            distinct_ref = OrderedDict()
            for line in lines[::-1]:
                unpack = line.split(' ')
                if len(unpack) < 3:
                    continue
                h, d, name = unpack
                if name.startswith("origin"):
                    name = name[7:]
                distinct_ref[h] = (d, h, name,)
            self.refs = distinct_ref
            logging.debug(f"find distinct ref {len(self.refs)}")
            eventbus.emit(eventbus.TOPIC_UPDATE_REF, self.refs)
            eventbus.emit(eventbus.TOPIC_CHECKOUT_MANIFEST, self.get(KEY_REF_HASH, 'master'))

    def update(self, c: dict):
        self.configs.update(c)

    def set_default(self):
        logging.debug(f"set default configs")
        if not self.configs.get(KEY_GIT_PATH):
            self.configs[KEY_GIT_PATH] = self.default_git()
        # if self.configs.get(KEY_REPO_PATH):
        #     self.check_refs()

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


_configs = Configs()


def init():
    _configs.read()
    _configs.set_default()


def write():
    _configs.write()


def init_url():
    return _configs.get(KEY_INIT_URL, '')


def repo_path():
    return _configs.get(KEY_REPO_PATH, '')


def git_path():
    return _configs.get(KEY_GIT_PATH, '')


def current_ref():
    return _configs.get(KEY_REF_HASH, '')


def manifest():
    return _configs.manifest


def refs():
    return _configs.refs


def check_refs():
    _configs.check_refs()
