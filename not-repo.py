import logging


class NotRepo:
    def __init__(self):
        pass

    def clone(self, path, target, progress):
        pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(threadName)s <%(module)s:%(lineno)d>[%(levelname)s]: %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S')
