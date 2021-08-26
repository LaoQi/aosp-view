import json
import logging
import os
import platform

import eventbus
from manifest import Manifest

CONFIG_PATH = os.path.join(os.path.expanduser('~'), ".aosp-view.json")
DEFAULT_MANIFEST_URL = 'https://android.googlesource.com/platform/manifest'

KEY_GIT_PATH = 'git_path'
KEY_INIT_URL = 'init_url'
KEY_REPO_PATH = 'repo_path'
KEY_REF_HASH = 'ref_hash'


class Configs:

    def __init__(self):
        self.configs = {}
        self.refs = {}
        self.manifest = Manifest()
        self.add_listener()

    def add_listener(self):
        eventbus.listen(eventbus.TOPIC_UPDATE_INIT_URL, lambda x: self.update({KEY_INIT_URL: x}))
        eventbus.listen(eventbus.TOPIC_UPDATE_GIT_PATH, lambda x: self.update({KEY_GIT_PATH: x}))
        eventbus.listen(eventbus.TOPIC_UPDATE_REPO_PATH, lambda x: self.update({KEY_REPO_PATH: x}))
        eventbus.listen(eventbus.TOPIC_CHECKOUT_MANIFEST_COMPLETE, lambda x: self.update({KEY_REF_HASH: x}))

        eventbus.listen(eventbus.TOPIC_UPDATE_MANIFEST, self.update_manifest)
        eventbus.listen(eventbus.TOPIC_UPDATE_REFS, self.update_refs)

    def update_manifest(self, content):
        self.manifest.set_content(content)
        eventbus.emit(eventbus.TOPIC_UPDATE_MANIFEST_COMPLETE)

    def update_refs(self, data):
        self.refs = data
        eventbus.emit(eventbus.TOPIC_UPDATE_REFS_COMPLETE)

    def update(self, c: dict):
        self.configs.update(c)

    def set_default(self):
        logging.debug(f"set default configs")
        if not self.configs.get(KEY_GIT_PATH):
            self.configs[KEY_GIT_PATH] = self.default_git()
        if not self.configs.get(KEY_INIT_URL):
            self.configs[KEY_INIT_URL] = DEFAULT_MANIFEST_URL

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


def base_url():
    # init url strip 'platform/manifest'
    url = _configs.get(KEY_INIT_URL, '')
    if len(url) < 17:
        raise Exception(f'base url error, {url}')
    return url[:-17]


def repo_path():
    return _configs.get(KEY_REPO_PATH, '')


def git_path():
    return _configs.get(KEY_GIT_PATH, '')


def ref_realpath(ref_hash):
    return os.path.realpath(os.path.join(repo_path(), _configs.refs.get(ref_hash)[2]))


def current_ref():
    return _configs.get(KEY_REF_HASH, '')


def current_ref_name():
    ref = _configs.get(KEY_REF_HASH, '')
    return _configs.refs.get(ref)[2]


def current_ref_realpath():
    return ref_realpath(_configs.get(KEY_REF_HASH, ''))


def project_realpath(project):
    return os.path.realpath(os.path.join(repo_path(), current_ref_realpath(), project.path))


def manifest_realpath():
    return os.path.realpath(os.path.join(repo_path(), 'manifest'))


def manifest():
    return _configs.manifest


def refs():
    return _configs.refs


def ref_name(ref_hash):
    return _configs.refs.get(ref_hash)[2]


def ready():
    return repo_path() != '' and git_path() != '' and init_url() != ''
