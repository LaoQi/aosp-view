import tkinter
from tkinter import filedialog, ttk

import configs
import eventbus
from locales import locales


class FormGroup(tkinter.Frame):
    def __init__(self, master, title, button_text=None, command=None, **kw):
        super().__init__(master, **kw)
        self.label = tkinter.Label(self, text=title, width=10)
        self.label.pack(side=tkinter.LEFT, padx=5)
        self.label.pack_propagate(0)

        if button_text:
            self.button = tkinter.Button(self, text=button_text, command=command)
            self.button.pack(side=tkinter.RIGHT, padx=5)
            self.button.pack_propagate(0)

    def disable(self):
        self.button.config(state=tkinter.DISABLED)

    def enable(self):
        self.button.config(state=tkinter.NORMAL)


class EntryGroup(FormGroup):
    def __init__(self, master, title, button_text=None, command=None, **kw):
        super().__init__(master, title, button_text, command, **kw)
        self.input = tkinter.Entry(self)
        self.input.pack(side=tkinter.LEFT, padx=5, expand=1, fill=tkinter.X)

    def disable(self):
        super().disable()
        self.input.config(state=tkinter.DISABLED)

    def enable(self):
        super().enable()
        self.input.config(state=tkinter.NORMAL)

    @property
    def value(self):
        return self.input.get()

    def set_value(self, v):
        self.input.delete(0, tkinter.END)
        self.input.insert(tkinter.END, v)


class ComboboxButtonGroup(FormGroup):
    def __init__(self, master, title, button_text=None, command=None, **kw):
        super().__init__(master, title, button_text, command, **kw)
        self.input = ttk.Combobox(self)
        self.input.pack(side=tkinter.LEFT, padx=5, expand=1, fill=tkinter.X)

    def disable(self):
        self.input.config(state=tkinter.DISABLED)

    def enable(self):
        self.input.config(state=tkinter.NORMAL)

    @property
    def value(self):
        return self.input.get()

    def set_value(self, v):
        self.input.set(v)


class PreferencesFrame(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.repo_path_entry = EntryGroup(self, locales.repo_path, locales.btn_setting, command=self.set_repo_path)
        self.repo_path_entry.pack(side=tkinter.TOP, padx=10, pady=10, expand=0, fill=tkinter.X)
        self.repo_path_entry.set_value(configs.repo_path())

        self.init_url_entry = EntryGroup(self, locales.init_url, locales.btn_update, command=self.init_load)
        self.init_url_entry.pack(side=tkinter.TOP, padx=10, pady=10, expand=0, fill=tkinter.X)
        self.init_url_entry.set_value(configs.init_url())

        self.git_path_entry = EntryGroup(self, locales.git_path, locales.btn_setting, command=self.set_git_path)
        self.git_path_entry.pack(side=tkinter.TOP, padx=10, pady=10, expand=0, fill=tkinter.X)
        self.git_path_entry.set_value(configs.git_path())

        self.tag_selector = ComboboxButtonGroup(self, locales.tag_selector, locales.checkout, command=None)
        self.tag_selector.pack(side=tkinter.TOP, padx=10, pady=10, expand=0, fill=tkinter.X)
        # self.tag_selector.set_value(configs.git_path())

        eventbus.ui_listen(eventbus.TOPIC_LOAD_CONFIG, self.modify_config)
        eventbus.ui_listen(eventbus.TOPIC_LOAD_INIT_FINISH, self.init_load_finish)

    def init_load(self):
        self.init_url_entry.disable()
        init_url = self.init_url_entry.value
        configs.update(dict(init_url=init_url))
        eventbus.emit(eventbus.TOPIC_LOG, f"fetch {init_url}")
        eventbus.emit(eventbus.TOPIC_LOAD_INIT, init_url)

    def init_load_finish(self, _):
        eventbus.emit(eventbus.TOPIC_LOG, f"update finish")
        self.init_url_entry.enable()

    def modify_config(self):
        self.repo_path_entry.set_value(configs.repo_path())
        self.init_url_entry.set_value(configs.init_url())

    def set_repo_path(self):
        path = filedialog.askdirectory()
        if path:
            self.repo_path_entry.set_value(path)
            configs.update(dict(repo_path=path))

    def set_git_path(self):
        openfile = filedialog.askopenfile()
        if openfile:
            self.git_path_entry.set_value(openfile.name)
            configs.update(dict(git_path=openfile.name))
