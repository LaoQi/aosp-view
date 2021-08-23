import tkinter

import eventbus
from locales import locales


class InfoFrame(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.label = tkinter.Label(self, text="the info")
        self.label.pack()

        button = tkinter.Button(self, text=locales.checkout, command=self.checkout)
        button.pack()

    def checkout(self):
        pass
