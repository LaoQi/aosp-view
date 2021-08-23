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

    @staticmethod
    def load_init(url):
        logging.debug(f"start update {url} {os.path.join(configs.repo_path(), 'manifest')}")

        cmd = [configs.git_path(), 'pull', '--force']
        kw = dict(cwd=os.path.join(configs.repo_path(), 'manifest'),
                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        if not os.path.exists(os.path.join(configs.repo_path(), 'manifest')):
            cmd = [
                configs.git_path(), 'clone', '--bare', configs.init_url(),
                os.path.join(configs.repo_path(), 'manifest')]
            kw['cwd'] = configs.repo_path()

        p = subprocess.Popen(cmd, **kw)

        while p.poll() is None:
            line = p.stdout.readline()
            while line:
                eventbus.emit(eventbus.TOPIC_LOG, line.decode())
                line = p.stdout.readline()

            time.sleep(0.01)

        eventbus.emit(eventbus.TOPIC_LOAD_INIT_FINISH)

    @staticmethod
    def checkout_manifest(ref):
        logging.debug(f"start checkout {ref}")

        try:
            result = subprocess.check_output(
                [configs.git_path(), 'cat-file', 'blob', f'{ref}:default.xml'],
                cwd=os.path.join(configs.repo_path(), 'manifest'))
            if not os.path.exists(os.path.join(configs.repo_path(), ref)):
                os.mkdir(os.path.join(configs.repo_path(), ref))

            eventbus.emit(eventbus.TOPIC_LOG, f'checkout {ref} complete')
            eventbus.emit(eventbus.TOPIC_CHECKOUT_MANIFEST_COMPLETE, ref)
            eventbus.emit(eventbus.TOPIC_UPDATE_MANIFEST, result.decode())
        except subprocess.CalledProcessError:
            eventbus.emit(eventbus.TOPIC_LOG, traceback.format_exc())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(threadName)s <%(module)s:%(lineno)d>[%(levelname)s]: %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S')
