import logging
import tkinter
from tkinter import ttk, messagebox, scrolledtext


class TreeView(tkinter.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.tree = ttk.Treeview(self)

        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        # xsb = ttk.Scrollbar(self.left_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set)
        # self.tree.configure(xscroll=xsb.set)
        # self.tree.heading('#0', text='', anchor='w')
        # xsb.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        ysb.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.tree.pack(side=tkinter.TOP, expand=1, fill=tkinter.BOTH, ipady=0)

        # try:
        #     root_node = self.tree.insert('', 'end', text='root', open=True)
        #     self._build_tree(root_node, self.nodes)
        # except Exception as e:
        #     messagebox.showerror(title='错误', message=str(e))

        # self.tree.bind('<<TreeviewOpen>>', self.open_node)
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
        self.notebook.add(tab1, text="All Projects")

        tab2 = DirectoryTree(self.notebook)
        self.notebook.add(tab2, text="Directory")

        tab3 = GroupsTree(self.notebook)
        self.notebook.add(tab3, text="Groups")

        self.notebook.pack(side=tkinter.TOP, expand=1, fill=tkinter.BOTH)


class LogsFrame(tkinter.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.text = scrolledtext.ScrolledText(self)

        self.text.pack(side=tkinter.LEFT, expand=1, fill=tkinter.BOTH)
        with open("demo.py", "r") as f:
            self.append(f.read())

    def append(self, msg):
        self.text.config(state=tkinter.NORMAL)
        self.text.insert(tkinter.END, msg)
        self.text.config(state=tkinter.DISABLED)
        self.text.see(tkinter.END)


class MainFrame:
    def __init__(self):
        self.master = tkinter.Tk()
        self.master.title("aosp-view")
        self.master.geometry('1280x640')
        self.master.iconbitmap("res/android_10_logo.ico")
        self.menubar = tkinter.Menu(self.master)
        self.master.config(menu=self.menubar)
        self.menubar.add_command(label='首选项', command=None)
        self.menubar.add_command(label='帮助', command=None)
        self.menubar.add_command(label='退出', command=self.master.quit)

        self.sidebar = Sidebar(self.master, width=300)
        # self.init_tree()
        self.sidebar.pack(side=tkinter.LEFT, fill=tkinter.Y)
        self.sidebar.pack_propagate(0)

        x_separator = tkinter.Frame(self.master,
                                    width=5, bd=5, relief=tkinter.SUNKEN,
                                    cursor="sb_h_double_arrow")
        x_separator.pack(side=tkinter.LEFT, fill=tkinter.Y, padx=0, pady=0)
        x_separator.bind('<B1-Motion>', self.resize_sidebar)

        self.right_frame = tkinter.Frame(self.master)

        self.right_top_frame = tkinter.Frame(self.right_frame, height=400)
        self.right_top_frame.pack(side=tkinter.TOP, fill=tkinter.BOTH)
        self.right_top_frame.pack_propagate(0)

        y_separator = tkinter.Frame(self.right_frame,
                                    height=5, bd=5, relief=tkinter.SUNKEN,
                                    cursor="sb_v_double_arrow")
        y_separator.pack(side=tkinter.TOP, fill=tkinter.X, padx=0, pady=0)
        y_separator.bind('<B1-Motion>', self.resize_right)

        self.logs_frame = LogsFrame(self.right_frame)
        self.logs_frame.pack(side=tkinter.BOTTOM, expand=1, fill=tkinter.BOTH)

        self.right_frame.pack(side=tkinter.RIGHT, expand=1, fill=tkinter.BOTH)
        self.right_frame.pack_propagate(0)

        self.status_bar = tkinter.Frame(self.right_frame)
        self.status_bar.pack(side=tkinter.TOP, expand=0, fill=tkinter.X)

    def resize_sidebar(self, event):
        width = self.sidebar.winfo_width() + event.x
        self.sidebar.configure(width=width)

    def resize_right(self, event):
        height = self.right_top_frame.winfo_height() + event.y
        self.right_top_frame.configure(height=height)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    MainFrame().master.mainloop()
