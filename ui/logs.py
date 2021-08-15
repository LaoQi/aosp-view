import tkinter
from tkinter import scrolledtext

import eventbus


class LogsFrame(tkinter.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.text = scrolledtext.ScrolledText(self)
        self.text.pack(side=tkinter.LEFT, expand=1, fill=tkinter.BOTH)
        self.text.config(state=tkinter.DISABLED)
        eventbus.ui_listen(eventbus.TOPIC_LOG, self.on_msg)

    def append(self, msg):
        self.text.config(state=tkinter.NORMAL)
        self.text.insert(tkinter.END, msg)
        self.text.config(state=tkinter.DISABLED)
        self.text.see(tkinter.END)

    def on_msg(self, event):
        self.append(f"{event}\n")
