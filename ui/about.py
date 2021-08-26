import tkinter

import webbrowser
import eventbus
from locales import locales


PROJECT_HOME = "https://github.com/LaoQi/aosp-view"


class AboutFrame(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master)
        label = tkinter.Label(self, text="Project Home")
        label.pack(side=tkinter.TOP, pady=50)

        link = tkinter.Label(self, text=PROJECT_HOME, fg="blue", cursor="hand2")
        link.pack(side=tkinter.TOP, pady=10)
        link.bind("<Button-1>", lambda e: self.openurl(PROJECT_HOME))

    @staticmethod
    def openurl(url):
        webbrowser.open(url)
