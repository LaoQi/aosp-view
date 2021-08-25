import tkinter
from tkinter import ttk

import eventbus


class StatusBar(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master, height=20)
        self.progressbar = ttk.Progressbar(self, length=200, mode='indeterminate', orient=tkinter.HORIZONTAL)
        self.progressbar.pack(side=tkinter.RIGHT, padx=20)
        label = tkinter.Label(self, text="statusbar")
        label.pack(side=tkinter.RIGHT, padx=20)

        eventbus.ui_listen(eventbus.TOPIC_CHECKOUT_PROJECT, self.progressbar_start)
        eventbus.ui_listen(eventbus.TOPIC_LOAD_INIT, self.progressbar_start)
        eventbus.ui_listen(eventbus.TOPIC_CHECKOUT_PROJECT_COMPLETE, self.progressbar_stop)
        eventbus.ui_listen(eventbus.TOPIC_LOAD_INIT_FINISH, self.progressbar_stop)

    def progressbar_start(self, _):
        self.progressbar.start(3)

    def progressbar_stop(self, _):
        self.progressbar.stop()
