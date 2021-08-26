import logging
import tkinter
from tkinter import scrolledtext

import eventbus


class LogsFrame(tkinter.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.last_line_index = 0
        self.text = scrolledtext.ScrolledText(self)
        self.text.pack(side=tkinter.LEFT, expand=1, fill=tkinter.BOTH)
        self.text.config(state=tkinter.DISABLED)
        eventbus.ui_listen(eventbus.TOPIC_LOG, self.on_message)

    def on_message(self, msg):
        self.last_line_index = self.text.index(tkinter.END)
        self.text.config(state=tkinter.NORMAL)
        self.text.insert(tkinter.END, f"{msg}\n")
        self.text.config(state=tkinter.DISABLED)
        self.text.see(tkinter.END)
