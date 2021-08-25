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

        self.project = None

        self.current_ref = tkinter.StringVar()
        self.revision = tkinter.StringVar()
        self.project_name = tkinter.StringVar()
        self.groups = tkinter.StringVar()
        self.checkout_path = tkinter.StringVar()

        i = iter(range(10))
        self.row(locales.current_ref, self.current_ref, next(i))
        self.row(locales.revision, self.revision, next(i))
        self.row(locales.project, self.project_name, next(i))
        self.row(locales.groups, self.groups, next(i))
        self.row(locales.checkout_path, self.checkout_path, next(i), link=True, command=self.open_project)

        eventbus.ui_listen(eventbus.TOPIC_SIDEBAR_SELECTED, self.on_project_selected)
        eventbus.ui_listen(eventbus.TOPIC_CHECKOUT_PROJECT_COMPLETE, self.on_project_complete)

    def row(self, title, str_var, row, link=False, command=None):
        label = tkinter.Label(self, text=title)
        label.grid(row=row, column=0, ipadx=10, ipady=5)

        if not link:
            label2 = tkinter.Label(self, textvariable=str_var, anchor=tkinter.W)
            label2.grid(row=row, column=1, ipadx=10, ipady=5, sticky=tkinter.W)
        else:
            label2 = tkinter.Label(self, textvariable=str_var, anchor=tkinter.W, fg="blue", cursor="hand2")
            label2.grid(row=row, column=1, ipadx=10, ipady=5, sticky=tkinter.W)
            label2.bind("<Button-1>", lambda e: command(e))

    def open_project(self, _):
        path = os.path.join(configs.repo_path(), configs.current_ref(), self.project.path)
        if os.path.exists(path):
            logging.debug(f"open directory {path}")
            webbrowser.open_new(path)
        else:
            logging.debug(f"checkout {path}")
            eventbus.emit(eventbus.TOPIC_LOG, f"checkout {configs.base_url()}{self.project.name}.git to {path}")
            eventbus.emit(eventbus.TOPIC_DISABLE_WINDOW)
            eventbus.emit(eventbus.TOPIC_CHECKOUT_PROJECT, self.project)

    def on_project_selected(self, project):
        self.project = project
        self.current_ref.set(configs.current_ref_name())
        self.revision.set(configs.manifest().default_revision)
        self.project_name.set(project.name)
        self.groups.set(" ".join(project.groups))

        self.checkout_path.set(locales.checkout)
        path = os.path.join(configs.repo_path(), configs.current_ref(), self.project.path)
        if os.path.exists(path):
            self.checkout_path.set(path)

    def on_project_complete(self, _):
        path = os.path.join(configs.repo_path(), configs.current_ref(), self.project.path)
        if os.path.exists(path):
            self.checkout_path.set(path)
        eventbus.emit(eventbus.TOPIC_ENABLE_WINDOW)

    def checkout(self):
        pass
