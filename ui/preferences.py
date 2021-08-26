import tkinter
from collections import OrderedDict
from tkinter import filedialog

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


class ListButtonGroup(FormGroup):
    def __init__(self, master, title, button_text=None, command=None, **kw):
        super().__init__(master, title, button_text, command, **kw)

        self.options = None
        self.selected = None

        frame = tkinter.Frame(self)
        frame.pack(side=tkinter.BOTTOM, padx=5, expand=1, fill=tkinter.X)

        self.search_input = tkinter.Entry(frame)
        self.search_input.pack(side=tkinter.TOP, padx=5, expand=1, fill=tkinter.X)
        self.search_input.bind('<KeyRelease>', self._update_options)

        sc = tkinter.Scrollbar(frame)
        sc.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.selector = tkinter.Listbox(frame, yscrollcommand=sc.set, font='TkFixedFont')
        self.selector.pack(side=tkinter.BOTTOM, padx=5, expand=1, fill=tkinter.X)
        sc.config(command=self.selector.yview)

    def disable(self):
        super().disable()
        self.search_input.config(state=tkinter.DISABLED)
        self.selector.config(state=tkinter.DISABLED)

    def enable(self):
        super().enable()
        self.search_input.config(state=tkinter.NORMAL)
        self.selector.config(state=tkinter.NORMAL)

    @property
    def value(self):
        index = self.selector.curselection()
        item = ''
        for i in index:
            item = self.selector.get(i)
        return item.strip('* ').split(' ')[1]

    def _update_options(self, _=None):
        self.selector.delete(0, tkinter.END)
        if self.options is None:
            return

        search_key = self.search_input.get()

        index = None
        count = 0
        for key, item in self.options.items():
            if search_key and search_key not in item[2] and search_key not in item[1]:
                continue

            item_name = f"   {item[0]} {item[1]} {item[2]}"
            if self.selected == item[1]:
                index = count
                item_name = f" * {item[0]} {item[1]} {item[2]}"
            self.selector.insert(tkinter.END, item_name)
            count += 1
        if index:
            self.selector.select_set(index)
            self.selector.yview_scroll(index, tkinter.UNITS)

    def set_options(self, options: OrderedDict, selected=None):
        self.options = options
        self.set_selected(selected)

    def set_selected(self, selected):
        self.selected = selected
        self._update_options()


class PreferencesFrame(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.repo_path_entry = EntryGroup(self, locales.repo_path, locales.btn_setting, command=self.set_repo_path)
        self.repo_path_entry.pack(side=tkinter.TOP, padx=10, pady=10, expand=0, fill=tkinter.X)
        self.repo_path_entry.set_value(configs.repo_path())

        self.init_url_entry = EntryGroup(self, locales.init_url, locales.btn_update, command=self.init_load)
        self.init_url_entry.pack(side=tkinter.TOP, padx=10, pady=10, expand=0, fill=tkinter.X)
        self.init_url_entry.set_value(configs.init_url())

        self.git_path_entry = EntryGroup(self, locales.git_executable, locales.btn_setting, command=self.set_git_path)
        self.git_path_entry.pack(side=tkinter.TOP, padx=10, pady=10, expand=0, fill=tkinter.X)
        self.git_path_entry.set_value(configs.git_path())

        self.ref_selector = ListButtonGroup(
            self, locales.ref_selector, locales.checkout, command=self.checkout_ref)

        self.ref_selector.pack(side=tkinter.TOP, padx=10, pady=10, expand=0, fill=tkinter.X)
        self.update_refs(0)
        # self.tag_selector.set_value(configs.git_path())

        eventbus.ui_listen(eventbus.TOPIC_LOAD_CONFIG, self.modify_config)
        eventbus.ui_listen(eventbus.TOPIC_LOAD_INIT_FINISH, self.init_load_finish)
        eventbus.ui_listen(eventbus.TOPIC_UPDATE_REFS_COMPLETE, self.update_refs)
        eventbus.ui_listen(eventbus.TOPIC_CHECKOUT_MANIFEST_COMPLETE, self.checkout_ref_complete)

    def init_load(self):
        self.init_url_entry.disable()
        init_url = self.init_url_entry.value
        eventbus.emit(eventbus.TOPIC_UPDATE_INIT_URL, init_url)
        eventbus.emit(eventbus.TOPIC_LOG, f"fetch {init_url}")
        eventbus.emit(eventbus.TOPIC_LOAD_INIT, init_url)
        eventbus.emit(eventbus.TOPIC_DISABLE_WINDOW)

    def init_load_finish(self, _):
        eventbus.emit(eventbus.TOPIC_LOG, f"update finish")
        eventbus.emit(eventbus.TOPIC_ENABLE_WINDOW)
        self.init_url_entry.enable()

    def modify_config(self):
        self.repo_path_entry.set_value(configs.repo_path())
        self.init_url_entry.set_value(configs.init_url())

    def set_repo_path(self):
        path = filedialog.askdirectory()
        if path:
            self.repo_path_entry.set_value(path)
            eventbus.emit(eventbus.TOPIC_UPDATE_REPO_PATH, path)

    def set_git_path(self):
        openfile = filedialog.askopenfile()
        if openfile:
            self.git_path_entry.set_value(openfile.name)
            eventbus.emit(eventbus.TOPIC_UPDATE_GIT_PATH, openfile.name)

    def update_refs(self, _):
        eventbus.emit(eventbus.TOPIC_LOG, f"check refs {configs.current_ref()}")
        self.ref_selector.set_options(configs.refs(), configs.current_ref())

    def checkout_ref(self):
        self.ref_selector.disable()
        ref_hash = self.ref_selector.value
        eventbus.emit(eventbus.TOPIC_CHECKOUT_MANIFEST, ref_hash)

    def checkout_ref_complete(self, _):
        self.ref_selector.enable()
        self.ref_selector.set_selected(configs.current_ref())
        eventbus.emit(eventbus.TOPIC_LOG, f"switch to ref {configs.current_ref()}")
