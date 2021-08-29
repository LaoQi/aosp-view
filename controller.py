
import logging
import os
import subprocess
import time
import traceback
from collections import OrderedDict

import configs
import eventbus


class Processor:
    @staticmethod
    def check_output(cmd, cwd):
        logging.debug(f"RunCommand: {subprocess.list2cmdline(cmd)}")
        eventbus.emit(eventbus.TOPIC_LOG, f"RunCommand: {subprocess.list2cmdline(cmd)}")
        try:
            p = subprocess.Popen(
                cmd, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                creationflags=0x08000000)
            result, _ = p.communicate()
            return result.decode()
        except Exception as e:
            logging.debug(e)
            eventbus.emit(eventbus.TOPIC_LOG, traceback.format_exc())

    @staticmethod
    def open(cmd, cwd, **kw):
        logging.debug(f"RunCommand: {subprocess.list2cmdline(cmd)}")
        eventbus.emit(eventbus.TOPIC_LOG, f"RunCommand: {subprocess.list2cmdline(cmd)}")
        try:
            p = subprocess.Popen(cmd, cwd=cwd,
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 creationflags=0x08000000, **kw)
            while p.poll() is None:
                line = p.stdout.readline()
                while line:
                    eventbus.emit(eventbus.TOPIC_LOG, line.decode())
                    line = p.stdout.readline()
                time.sleep(0.01)
        except Exception as e:
            logging.debug(e)
            eventbus.emit(eventbus.TOPIC_LOG, traceback.format_exc())

    @staticmethod
    def run(cmd, cwd, **kw):
        logging.debug(f"RunCommand: {subprocess.list2cmdline(cmd)}")
        try:
            p = subprocess.Popen(cmd, cwd=cwd,
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 creationflags=0x08000000, **kw)
            status = p.wait()
            logging.debug(f"Command result {status}")
            eventbus.emit(eventbus.TOPIC_LOG, f"Command result {status}")
            return status == 0
        except Exception as e:
            logging.debug(e)
            return False


class Controller:
    def __init__(self):
        eventbus.listen(eventbus.TOPIC_LOAD_INIT, self.load_init)
        eventbus.listen(eventbus.TOPIC_LOAD_INIT_FINISH, lambda x: self.check_refs(x))
        eventbus.listen(eventbus.TOPIC_CHECKOUT_MANIFEST, lambda x: self.checkout_manifest(x))
        eventbus.listen(eventbus.TOPIC_CHECKOUT_PROJECT, self.checkout_project)

        eventbus.listen(eventbus.TOPIC_GUI_COMPLETE, self.check_refs)

    def load_init(self, url):
        logging.debug(f"start update {url} {configs.manifest_realpath()}")

        cmd = [
            configs.git_path(), 'clone', '--bare', configs.init_url(),
            configs.manifest_realpath()]
        cwd = configs.repo_path()

        if os.path.exists(configs.manifest_realpath()):
            self._check_init_url(url)
            cmd = [configs.git_path(), 'fetch']
            cwd = configs.manifest_realpath()

        Processor.open(cmd, cwd)
        eventbus.emit(eventbus.TOPIC_LOAD_INIT_FINISH)

    @staticmethod
    def _check_init_url(url):
        result = Processor.check_output(
            [configs.git_path(), 'config', 'remote.origin.url'],
            cwd=configs.manifest_realpath())
        current_url = result.strip()
        logging.debug(f"Current remote {current_url} compare to {url} {current_url == url}")
        if current_url != url.strip():
            Processor.check_output(
                [configs.git_path(), 'config', 'remote.origin.url', url],
                cwd=configs.manifest_realpath())
            eventbus.emit(eventbus.TOPIC_LOG, f"reset remote {current_url} ==> {url}")

    @staticmethod
    def check_refs(_):
        if os.path.exists(configs.manifest_realpath()):

            result = Processor.check_output(
                [configs.git_path(), 'rev-parse', '--short', 'HEAD'], configs.manifest_realpath())
            current_ref = result.strip()
            old_ref = configs.current_ref()
            if old_ref != '':
                result = Processor.run(
                    [configs.git_path(), 'cat-file', '-p', old_ref], configs.manifest_realpath())
                if result:
                    current_ref = old_ref

            # logging.debug(f"find current ref {self.current_ref}")
            # eventbus.emit(eventbus.TOPIC_UPDATE_CURRENT_REF, self.current_ref)

            # result = subprocess.check_output([self.get(KEY_GIT_PATH, ''), 'tag', '-l'],
            #                                  cwd=os.path.join(self.get(KEY_REPO_PATH, ''), 'manifest'))

            result = Processor.check_output([
                configs.git_path(), 'branch', '-a',
                '--format=%(objectname:short) %(creatordate:short) %(refname)', '--sort=creatordate'
            ], configs.manifest_realpath())
            lines = result.strip().split('\n')
            distinct_ref = OrderedDict()
            for line in lines[::-1]:
                unpack = line.split(' ')
                if len(unpack) < 3:
                    continue
                h, d, name = unpack
                distinct_ref[h] = (d, h, name[11:])  # strip "/ref/heads/"
            logging.debug(f"find ref {len(distinct_ref)}")
            eventbus.emit(eventbus.TOPIC_UPDATE_REFS, distinct_ref)
            eventbus.emit(eventbus.TOPIC_CHECKOUT_MANIFEST, current_ref)

    @staticmethod
    def checkout_manifest(ref_hash):
        logging.debug(f"start checkout {ref_hash}")

        result = Processor.check_output(
            [configs.git_path(), 'cat-file', 'blob', f'{ref_hash}:default.xml'],
            cwd=configs.manifest_realpath())
        if not os.path.exists(configs.ref_realpath(ref_hash)):
            logging.debug(f"make directory {configs.ref_realpath(ref_hash)}")
            os.mkdir(configs.ref_realpath(ref_hash))

        eventbus.emit(eventbus.TOPIC_LOG, f'checkout {ref_hash} complete')
        eventbus.emit(eventbus.TOPIC_CHECKOUT_MANIFEST_COMPLETE, ref_hash)
        eventbus.emit(eventbus.TOPIC_UPDATE_MANIFEST, result)

    @staticmethod
    def checkout_project(project):
        logging.debug(f"start checkout {project.name} {project.revision}")
        ref = project.revision
        if ref.startswith("refs"):
            ref = ref.split("/")[-1]
        Processor.open([
            configs.git_path(), 'clone', '--depth=1', '-q', project.url,
            '-b', ref,
            configs.project_realpath(project),
        ], cwd=configs.current_ref_realpath())

        eventbus.emit(eventbus.TOPIC_LOG, f"checkout {project.name} {project.revision} complete")
        eventbus.emit(eventbus.TOPIC_CHECKOUT_PROJECT_COMPLETE)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(threadName)s <%(module)s:%(lineno)d>[%(levelname)s]: %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S')
