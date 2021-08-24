import logging
import queue
import threading
import traceback

TOPIC_LOG = 'logs'
TOPIC_LOAD_INIT = 'load_init'
TOPIC_LOAD_INIT_FINISH = 'load_init_finish'
TOPIC_LOAD_CONFIG = 'load_config'

TOPIC_GUI_COMPLETE = 'gui_complete'

TOPIC_UPDATE_INIT_URL = 'update_init_url'
TOPIC_UPDATE_GIT_PATH = 'update_git_path'
TOPIC_UPDATE_REPO_PATH = 'update_repo_path'
TOPIC_UPDATE_MANIFEST = 'update_manifest'

TOPIC_UPDATE_REF = 'update_ref'
TOPIC_UPDATE_CURRENT_REF = 'update_current_ref'

TOPIC_UPDATE_MANIFEST_COMPLETE = 'update_manifest_complete'

TOPIC_CHECKOUT_MANIFEST = 'checkout_manifest'
TOPIC_CHECKOUT_MANIFEST_COMPLETE = 'checkout_manifest_complete'

TOPIC_SWITCH_TABS = 'switch_tabs'

TOPIC_SIDEBAR_SEARCH = 'sidebar_search'


class Handler:
    def __init__(self, func):
        self.func = func

    def task(self, args):
        def func():
            self.func(args)

        return func


class UIHandler(Handler):
    pass


class EventBus(threading.Thread):
    def __init__(self):
        super().__init__(name="EventBus", daemon=True)
        self.queue = queue.Queue()
        self.ui_queue = None
        self.listeners = dict()

    def add_listener(self, topic: str, listener):
        if self.listeners.get(topic):
            self.listeners.get(topic).append(listener)
        else:
            self.listeners[topic] = [listener]

    def _do_ui_task(self, handler, args):
        if self.ui_queue:
            self.ui_queue.put(handler.task(args))

    def dispatch(self, topic, event=None):
        for handler in self.listeners.get(topic, []):
            if isinstance(handler, UIHandler):
                _bus._do_ui_task(handler, event)
            elif isinstance(handler, Handler):
                self.queue.put(handler.task(event))
            elif callable(handler):
                handler(event)

    def run(self) -> None:
        logging.debug("start event bus")
        while True:
            try:
                task = self.queue.get()
                task()
            except Exception as e:
                logging.warning(e)
                self.dispatch(TOPIC_LOG, traceback.format_exc())


_bus = EventBus()


def listen(topic, func):
    _bus.add_listener(topic, Handler(func))


def ui_listen(topic, func):
    _bus.add_listener(topic, UIHandler(func))


def set_ui_queue(q):
    _bus.ui_queue = q


def emit(topic, event=None):
    _bus.dispatch(topic, event)


def emit_func(topic, event=None):
    def func():
        emit(topic, event)
    return func


def start():
    _bus.start()
