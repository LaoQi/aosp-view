
import logging
import os
import subprocess
import time
import traceback

import configs
import eventbus


class Controller:
    def __init__(self):
        eventbus.listen(eventbus.TOPIC_LOAD_INIT, self.load_init)
        eventbus.listen(eventbus.TOPIC_LOAD_INIT_FINISH, lambda x: configs.check_refs())
        eventbus.listen(eventbus.TOPIC_CHECKOUT_MANIFEST, lambda x: self.checkout_manifest(x))
        eventbus.listen(eventbus.TOPIC_CHECKOUT_PROJECT, self.checkout_project)

    def load_init(self, url):
        logging.debug(f"start update {url} {os.path.join(configs.repo_path(), 'manifest')}")

        cmd = [
            configs.git_path(), 'clone', '--bare', configs.init_url(),
            os.path.join(configs.repo_path(), 'manifest')]
        kw = dict(cwd=configs.repo_path(),
                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        if os.path.exists(os.path.join(configs.repo_path(), 'manifest')):
            self._check_init_url(url)
            cmd = [configs.git_path(), 'fetch']
            kw['cwd'] = os.path.join(configs.repo_path(), 'manifest')

        try:
            p = subprocess.Popen(cmd, **kw)

            while p.poll() is None:
                line = p.stdout.readline()
                while line:
                    eventbus.emit(eventbus.TOPIC_LOG, line.decode())
                    line = p.stdout.readline()

                time.sleep(0.01)
        except Exception as e:
            logging.debug(e)
            eventbus.emit(eventbus.TOPIC_LOG, traceback.format_exc())

        eventbus.emit(eventbus.TOPIC_LOAD_INIT_FINISH)

    @staticmethod
    def _check_init_url(url):
        try:
            result = subprocess.check_output(
                [configs.git_path(), 'config', 'remote.origin.url'],
                cwd=os.path.join(configs.repo_path(), 'manifest'))
            current_url = result.decode().strip()
            logging.debug(f"Current remote {current_url} compare to {url} {current_url == url}")
            if current_url != url.strip():
                subprocess.check_output(
                    [configs.git_path(), 'config', 'remote.origin.url', url],
                    cwd=os.path.join(configs.repo_path(), 'manifest'))
                eventbus.emit(eventbus.TOPIC_LOG, f"reset remote {current_url} ==> {url}")
        except subprocess.CalledProcessError:
            eventbus.emit(eventbus.TOPIC_LOG, traceback.format_exc())

    @staticmethod
    def checkout_manifest(ref):
        logging.debug(f"start checkout {ref}")

        try:
            result = subprocess.check_output(
                [configs.git_path(), 'cat-file', 'blob', f'{ref}:default.xml'],
                cwd=os.path.join(configs.repo_path(), 'manifest'))
            if not os.path.exists(os.path.join(configs.repo_path(), ref)):
                logging.debug(f"make directory {os.path.join(configs.repo_path(), ref)}")
                os.mkdir(os.path.join(configs.repo_path(), ref))

            eventbus.emit(eventbus.TOPIC_LOG, f'checkout {ref} complete')
            eventbus.emit(eventbus.TOPIC_CHECKOUT_MANIFEST_COMPLETE, ref)
            eventbus.emit(eventbus.TOPIC_UPDATE_MANIFEST, result.decode())
        except subprocess.CalledProcessError:
            eventbus.emit(eventbus.TOPIC_LOG, traceback.format_exc())

    @staticmethod
    def checkout_project(project):
        logging.debug(f"start checkout {project.name}")
        try:
            p = subprocess.Popen([
                configs.git_path(), 'clone', '--depth=1', '-q', f"{configs.base_url()}{project.name}.git",
                '-b', configs.manifest().default_revision,
                os.path.join(configs.repo_path(), configs.current_ref(), project.path),
            ],
                cwd=os.path.join(configs.repo_path(), configs.current_ref()),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            while p.poll() is None:
                line = p.stdout.readline()
                while line:
                    eventbus.emit(eventbus.TOPIC_LOG, line.decode())
                    line = p.stdout.readline()
        except Exception as e:
            logging.debug(e)
            eventbus.emit(eventbus.TOPIC_LOG, traceback.format_exc())

        eventbus.emit(eventbus.TOPIC_LOG, f"checkout {project.name} complete")
        eventbus.emit(eventbus.TOPIC_CHECKOUT_PROJECT_COMPLETE)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(threadName)s <%(module)s:%(lineno)d>[%(levelname)s]: %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S')
