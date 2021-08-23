import logging
import queue
import tkinter
import traceback
from tkinter import ttk

import configs
import eventbus
from locales import locales
from ui.information import InfoFrame
from ui.logs import LogsFrame
from ui.preferences import PreferencesFrame
from ui.sidebar import Sidebar
from ui.statusbar import StatusBar


class ManageFrame(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master, height=400)
        self.notebook = ttk.Notebook(self)

        tab1 = InfoFrame(self.notebook)
        self.notebook.add(tab1, text=locales.info)

        tab2 = PreferencesFrame(self.notebook)
        self.notebook.add(tab2, text=locales.preferences)

        self.notebook.pack(side=tkinter.TOP, expand=1, fill=tkinter.BOTH)

        eventbus.ui_listen(eventbus.TOPIC_SWITCH_TABS, self.switch_tabs)

    def switch_tabs(self, index):
        self.notebook.select(index)


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


class Window:
    def __init__(self):
        self.queue = queue.Queue()
        eventbus.set_ui_queue(self.queue)

        self.master = tkinter.Tk()
        self.master.title("aosp-view")
        self.master.geometry('1280x640')
        self.master.minsize(800, 600)
        self.master.iconbitmap("res/android_10_logo.ico")
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

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

    def on_close(self):
        configs.write()
        self.master.quit()

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
        self.master.after(1, eventbus.emit_func(eventbus.TOPIC_GUI_COMPLETE))
        self.master.mainloop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    Window().mainloop()
