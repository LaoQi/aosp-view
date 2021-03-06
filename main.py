# coding:utf-8
import logging

import configs
import eventbus
from controller import Controller
from ui import Window


def main():
    eventbus.start()
    configs.init()
    Controller()
    Window().mainloop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(threadName)s <%(module)s:%(lineno)d>[%(levelname)s]: %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S')
    main()
