import logging
from time import sleep

import eventbus


class Controller:
    def __init__(self):
        eventbus.listen(eventbus.TOPIC_LOAD_INIT, self.load_init)

    def load_init(self, url):
        logging.debug(f"start update {url}")

        eventbus.emit(eventbus.TOPIC_LOAD_INIT_FINISH)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(threadName)s <%(module)s:%(lineno)d>[%(levelname)s]: %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S')

