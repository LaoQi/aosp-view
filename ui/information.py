import tkinter

import eventbus
from locales import locales


class InfoFrame(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master)

        i = iter(range(10))
        self.form_title(locales.current_ref, next(i))
        self.form_title(locales.project, next(i))
        self.form_title(locales.groups, next(i))
        self.form_title(locales.checkout_path, next(i))

        # button = tkinter.Button(self, text=locales.checkout, command=self.checkout)
        # button.g()

    def form_title(self, text, row):
        label = tkinter.Label(self, text=text)
        label.grid(row=row, column=0, ipadx=10, ipady=5)

    def checkout(self):
        pass
