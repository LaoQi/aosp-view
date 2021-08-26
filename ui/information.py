import logging
import os
import tkinter
import webbrowser

import configs
import eventbus
from locales import locales


class InfoFrame(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.panel = tkinter.Frame(self, padx=30, pady=30)
        self.panel.pack(side=tkinter.LEFT, expand=tkinter.YES, fill=tkinter.BOTH)

        self.project = None

        self.current_ref = tkinter.StringVar()
        self.revision = tkinter.StringVar()
        self.project_name = tkinter.StringVar()
        self.groups = tkinter.StringVar()
        self.git_url = tkinter.StringVar()
        self.checkout_path = tkinter.StringVar()

        i = iter(range(10))
        self.row_label(locales.current_ref, self.current_ref, next(i))
        self.row_label(locales.revision, self.revision, next(i))
        self.row_label(locales.project, self.project_name, next(i))
        self.row_label(locales.groups, self.groups, next(i))
        self.row_text(locales.git_url, self.git_url, next(i))
        self.row_link(locales.checkout_path, self.checkout_path, next(i), command=self.open_project)

        eventbus.ui_listen(eventbus.TOPIC_SIDEBAR_SELECTED, self.on_project_selected)
        eventbus.ui_listen(eventbus.TOPIC_CHECKOUT_PROJECT_COMPLETE, self.on_project_complete)

    def row_label(self, title, str_var, row):
        root = self.panel
        label = tkinter.Label(root, text=title)
        label.grid(row=row, column=0, ipadx=10, ipady=5)

        label2 = tkinter.Label(root, textvariable=str_var, anchor=tkinter.W, padx=10, pady=5)
        label2.grid(row=row, column=1, sticky=tkinter.W)

    def row_link(self, title, str_var, row, command=None):
        root = self.panel
        label = tkinter.Label(root, text=title)
        label.grid(row=row, column=0, ipadx=10, ipady=5)

        label2 = tkinter.Label(root, textvariable=str_var, anchor=tkinter.W, padx=10, pady=5, fg="blue",
                               cursor="hand2")
        label2.grid(row=row, column=1, sticky=tkinter.W)
        label2.bind("<Button-1>", lambda e: command(e))

    def row_text(self, title, str_var, row):
        root = self.panel
        label = tkinter.Label(root, text=title)
        label.grid(row=row, column=0, ipadx=10, ipady=5)

        text = tkinter.Entry(root, textvariable=str_var, width=400)
        text.configure(state='readonly', relief='flat')
        text.grid(row=row, column=1, sticky=tkinter.W, padx=10, pady=5)

    def open_project(self, _):
        path = configs.project_realpath(self.project)
        if os.path.exists(path):
            logging.debug(f"open directory {path}")
            webbrowser.open_new(path)
        else:
            logging.debug(f"checkout {path}")
            eventbus.emit(eventbus.TOPIC_LOG, f"checkout {self.project.url} to {path}")
            eventbus.emit(eventbus.TOPIC_DISABLE_WINDOW)
            eventbus.emit(eventbus.TOPIC_CHECKOUT_PROJECT, self.project)

    def on_project_selected(self, project):
        self.project = project
        self.current_ref.set(configs.current_ref_name())
        self.revision.set(project.revision)
        self.project_name.set(project.name)
        self.git_url.set(project.url)
        self.groups.set(" ".join(project.groups))

        self.checkout_path.set(locales.checkout)
        path = configs.project_realpath(project)
        if os.path.exists(path):
            self.checkout_path.set(path)

    def on_project_complete(self, _):
        path = configs.project_realpath(self.project)
        if os.path.exists(path):
            self.checkout_path.set(path)
        eventbus.emit(eventbus.TOPIC_ENABLE_WINDOW)

    def checkout(self):
        pass
