import logging
import queue
import tkinter
import traceback
from tkinter import ttk

import configs
import eventbus
from locales import locales
from ui.about import AboutFrame
from ui.information import InfoFrame
from ui.logs import LogsFrame
from ui.preferences import PreferencesFrame
from ui.sidebar import Sidebar
from ui.statusbar import StatusBar


class ManageFrame(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.notebook = ttk.Notebook(self)

        tab1 = InfoFrame(self.notebook)
        self.notebook.add(tab1, text=locales.info)

        tab2 = PreferencesFrame(self.notebook)
        self.notebook.add(tab2, text=locales.preferences)

        tab3 = AboutFrame(self.notebook)
        self.notebook.add(tab3, text=locales.about)

        self.notebook.pack(side=tkinter.TOP, expand=1, fill=tkinter.BOTH)

        eventbus.ui_listen(eventbus.TOPIC_SWITCH_MAIN_TABS, self.switch_tabs)

    def switch_tabs(self, index):
        self.notebook.select(index)


class MainFrame(tkinter.PanedWindow):
    def __init__(self, master):
        super().__init__(master, orient=tkinter.HORIZONTAL)

        self.sidebar = Sidebar(self)
        self.add(self.sidebar, width=400)

        self.right = tkinter.PanedWindow(self, orient=tkinter.VERTICAL)
        self.add(self.right)

        self.manage_frame = ManageFrame(self.right)
        self.right.add(self.manage_frame, height=400)

        self.logs_frame = LogsFrame(self.right)
        self.right.add(self.logs_frame)


class Window:
    def __init__(self):
        self.queue = queue.Queue()
        eventbus.set_ui_queue(self.queue)

        self.master = tkinter.Tk()
        self.master.title("aosp-view")
        self.master.geometry('1280x800')
        self.master.minsize(1024, 800)
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

        eventbus.ui_listen(eventbus.TOPIC_DISABLE_WINDOW, lambda _: self.disable())
        eventbus.ui_listen(eventbus.TOPIC_ENABLE_WINDOW, lambda _: self.enable())

    def on_close(self):
        configs.write()
        self.master.quit()

    def disable(self):
        # self.master.configure(cursor="watch")  # Non-operative
        self.master.attributes('-disabled', 1)

    def enable(self):
        # self.master.configure(cursor="arrow")  # Non-operative
        self.master.attributes('-disabled', 0)

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

    @staticmethod
    def on_gui_complete():
        eventbus.emit(eventbus.TOPIC_GUI_COMPLETE)
        if not configs.ready():
            eventbus.emit(eventbus.TOPIC_SWITCH_MAIN_TABS, 1)

    def mainloop(self):
        self.master.after(50, self.update)
        self.master.after(1, self.on_gui_complete)
        self.master.mainloop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    Window().mainloop()
