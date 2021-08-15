import logging
import tkinter
from tkinter import ttk

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

    def select_node(self, _):
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
