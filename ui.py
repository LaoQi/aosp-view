import logging
import queue
import tkinter
import traceback
from tkinter import ttk, scrolledtext, filedialog

import configs
import eventbus
from locales import locales


class TreeView(tkinter.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.tree = ttk.Treeview(self)

        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        # xsb = ttk.Scrollbar(self.left_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set)
        # self.tree.heading('#0', text='', anchor='w')
        # xsb.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        ysb.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.tree.pack(side=tkinter.TOP, expand=1, fill=tkinter.BOTH, ipady=0)

        # try:
        #     root_node = self.tree.insert('', 'end', text='root', open=True)
        #     self._build_tree(root_node, self.nodes)
        # except Exception as e:
        #     messagebox.showerror(title='错误', message=str(e))
        self.tree.bind('<<TreeviewSelect>>', self.select_node)
        self.pack(side=tkinter.TOP, expand=1, fill=tkinter.BOTH)

    def select_node(self, event):
        node = self.tree.focus()
        logging.debug(f"select node {node}")


class DirectoryTree(TreeView):
    def __init__(self, master):
        super().__init__(master)


class AllProjectsTree(TreeView):
    def __init__(self, master):
        super().__init__(master)


class GroupsTree(TreeView):
    def __init__(self, master):
        super().__init__(master)


class Sidebar(tkinter.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.nodes = []

        self.search_entry = tkinter.Entry(self)
        self.search_entry.pack(side=tkinter.TOP, expand=0, fill=tkinter.X)

        self.notebook = ttk.Notebook(self)

        tab1 = AllProjectsTree(self.notebook)
        self.notebook.add(tab1, text=locales.all_projects)

        tab2 = DirectoryTree(self.notebook)
        self.notebook.add(tab2, text=locales.directory)

        tab3 = GroupsTree(self.notebook)
        self.notebook.add(tab3, text=locales.groups)

        self.notebook.pack(side=tkinter.TOP, expand=1, fill=tkinter.BOTH)


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


class EntryGroup(tkinter.Frame):
    def __init__(self, master, title, **kw):
        super().__init__(master, **kw)
        self.label = tkinter.Label(self, text=title, width=10)
        self.label.pack(side=tkinter.LEFT, padx=5)
        self.label.pack_propagate(0)
        self.entry = tkinter.Entry(self)
        self.entry.pack(side=tkinter.LEFT, padx=5, expand=1, fill=tkinter.X)

    def disable(self):
        self.entry.config(state=tkinter.DISABLED)

    def enable(self):
        self.entry.config(state=tkinter.NORMAL)

    @property
    def value(self):
        return self.entry.get()

    def set_value(self, v):
        self.entry.delete(0, tkinter.END)
        self.entry.insert(tkinter.END, v)


class EntryButtonGroup(EntryGroup):
    def __init__(self, master, title, button_text, command, **kw):
        super().__init__(master, title, **kw)
        self.button = tkinter.Button(self, text=button_text, command=command)
        self.button.pack(side=tkinter.RIGHT, padx=5)
        self.button.pack_propagate(0)

    def disable(self):
        super(EntryButtonGroup, self).disable()
        self.button.config(state=tkinter.DISABLED)

    def enable(self):
        super(EntryButtonGroup, self).enable()
        self.button.config(state=tkinter.NORMAL)


class PreferencesFrame(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.repo_path_entry = EntryButtonGroup(self, locales.repo_path, locales.btn_setting, command=self.set_repo_path)
        self.repo_path_entry.pack(side=tkinter.TOP, padx=10, pady=10, expand=0, fill=tkinter.X)
        self.repo_path_entry.set_value(configs.get().repo_path)

        self.init_url_entry = EntryButtonGroup(self, locales.init_url, locales.btn_update, command=self.init_load)
        self.init_url_entry.pack(side=tkinter.TOP, padx=10, pady=10, expand=0, fill=tkinter.X)
        self.init_url_entry.set_value(configs.get().init_url)

        self.git_path_entry = EntryButtonGroup(self, locales.git_path, locales.btn_setting, command=self.set_git_path)
        self.git_path_entry.pack(side=tkinter.TOP, padx=10, pady=10, expand=0, fill=tkinter.X)
        self.git_path_entry.set_value(configs.get().git_path)

        eventbus.ui_listen(eventbus.TOPIC_LOAD_CONFIG, self.modify_config)
        eventbus.ui_listen(eventbus.TOPIC_LOAD_INIT_FINISH, self.init_load_finish)

    def init_load(self):
        self.init_url_entry.disable()
        eventbus.emit(eventbus.TOPIC_LOG, f"fetch {self.init_url_entry.value}")
        eventbus.emit(eventbus.TOPIC_LOAD_INIT, self.init_url_entry.value)

    def init_load_finish(self, _):
        eventbus.emit(eventbus.TOPIC_LOG, f"update finish")
        self.init_url_entry.enable()

    def modify_config(self):
        self.repo_path_entry.set_value(configs.get().repo_path)
        self.init_url_entry.set_value(configs.get().init_url)

    def set_repo_path(self):
        path = filedialog.askdirectory()
        logging.debug(path)
        self.repo_path_entry.set_value(path)

    def set_git_path(self):
        path = filedialog.askopenfile()
        logging.debug(path)
        self.git_path_entry.set_value(path.name)


class InfoFrame(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.label = tkinter.Label(self, text="the info")
        self.label.pack()


class ManageFrame(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master, height=400)
        self.notebook = ttk.Notebook(self)

        tab1 = InfoFrame(self.notebook)
        self.notebook.add(tab1, text=locales.info)

        tab2 = PreferencesFrame(self.notebook)
        self.notebook.add(tab2, text=locales.preferences)

        self.notebook.pack(side=tkinter.TOP, expand=1, fill=tkinter.BOTH)


class MainFrame(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.sidebar = Sidebar(self, width=300)
        # self.init_tree()
        self.sidebar.pack(side=tkinter.LEFT, fill=tkinter.Y)
        self.sidebar.pack_propagate(0)

        x_separator = tkinter.Frame(self,
                                    width=5, bd=5, relief=tkinter.SUNKEN,
                                    cursor="sb_h_double_arrow")
        x_separator.pack(side=tkinter.LEFT, fill=tkinter.Y, padx=0, pady=0)
        x_separator.bind('<B1-Motion>', self.resize_sidebar)

        self.right_frame = tkinter.Frame(self)

        self.manage_frame = ManageFrame(self.right_frame)
        self.manage_frame.pack(side=tkinter.TOP, fill=tkinter.BOTH)
        self.manage_frame.pack_propagate(0)

        y_separator = tkinter.Frame(self.right_frame,
                                    height=5, bd=5, relief=tkinter.SUNKEN,
                                    cursor="sb_v_double_arrow")
        y_separator.pack(side=tkinter.TOP, fill=tkinter.X, padx=0, pady=0)
        y_separator.bind('<B1-Motion>', self.resize_manage)

        self.logs_frame = LogsFrame(self.right_frame)
        self.logs_frame.pack(side=tkinter.BOTTOM, expand=1, fill=tkinter.BOTH)

        self.right_frame.pack(side=tkinter.RIGHT, expand=1, fill=tkinter.BOTH)
        self.right_frame.pack_propagate(0)

        self.bind('<Configure>', self.resize)

    def resize_sidebar(self, event):
        total = self.winfo_width()
        width = self.sidebar.winfo_width() + event.x
        if width < 150:
            width = 150
        elif width > total - 400:
            width = total - 400
        self.sidebar.configure(width=width)

    def resize_manage(self, event):
        total = self.winfo_height()
        height = self.manage_frame.winfo_height() + event.y
        if height < 100:
            height = 100
        elif height > total - 100:
            height = total - 100
        self.manage_frame.configure(height=height)

    def resize(self, event):
        total_height = self.winfo_height()
        manage_height = self.manage_frame.winfo_height() + event.y
        if manage_height > total_height - 100:
            manage_height = total_height - 100
            self.manage_frame.configure(height=manage_height)

        total_width = self.winfo_width()
        sidebar_width = self.sidebar.winfo_width() + event.x
        if sidebar_width > total_width - 400:
            sidebar_width = total_width - 400
            self.sidebar.configure(width=sidebar_width)


class StatusBar(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master, height=20)
        label = tkinter.Label(self, text="statusbar")
        label.pack()


class Window:
    def __init__(self):
        self.queue = queue.Queue()
        eventbus.set_ui_queue(self.queue)

        self.master = tkinter.Tk()
        self.master.title("aosp-view")
        self.master.geometry('1280x640')
        self.master.minsize(800, 600)
        self.master.iconbitmap("res/android_10_logo.ico")

        # self.menubar = tkinter.Menu(self.master)
        # self.master.config(menu=self.menubar)
        # self.menubar.add_command(label=locales.preferences, command=None)
        # self.menubar.add_command(label=locales.help, command=None)
        # self.menubar.add_command(label='退出', command=self.master.quit)

        self.main = MainFrame(self.master)
        self.main.pack(side=tkinter.TOP, expand=1, fill=tkinter.BOTH)

        self.status_bar = StatusBar(self.master)
        self.status_bar.pack(side=tkinter.BOTTOM, expand=0, fill=tkinter.X)
        self.status_bar.pack_propagate(0)

    def update(self):
        task = None
        try:
            task = self.queue.get_nowait()
        except queue.Empty:
            pass
        if callable(task):
            try:
                task()
            except Exception as e:
                logging.exception(e)
                eventbus.emit(eventbus.TOPIC_LOG, traceback.format_exc())
        self.master.after(50, self.update)

    def mainloop(self):
        self.master.after(50, self.update)
        self.master.mainloop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    Window().mainloop()
