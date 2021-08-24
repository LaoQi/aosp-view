import logging
import tkinter
from tkinter import ttk

import configs
import eventbus
from locales import locales


class TreeView(tkinter.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.tree = ttk.Treeview(self)
        self.data = []
        self.mapping = {}

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
        eventbus.emit(eventbus.TOPIC_SWITCH_TABS, 0)
        if node in self.mapping:
            logging.debug(f"select node {self.mapping[node]}")

    def clear(self):
        children = self.tree.get_children()
        for child in children:
            self.tree.delete(child)
        self.mapping.clear()

    def refresh_tree(self, keyword=None):
        pass

    def update_items(self, _):
        pass


class DirectoryTree(TreeView):
    def __init__(self, master):
        super().__init__(master)
        self.tree.heading('#0', text=locales.directory, anchor='w')
        eventbus.ui_listen(eventbus.TOPIC_UPDATE_MANIFEST_COMPLETE, self.update_items)
        eventbus.ui_listen(eventbus.TOPIC_SIDEBAR_SEARCH, self.refresh_tree)

    def refresh_tree(self, keyword=None):
        self.clear()
        for project in self.data:
            if keyword and keyword not in project.name:
                continue
            last_slash = project.path.rfind('/')
            if last_slash < 0:
                identifier = self.tree.insert('', tkinter.END, project.path, text=project.path)
                self.mapping[identifier] = project
            else:
                root = ''
                for path in project.path.split('/')[:-1]:
                    next_root = f"{root}{path}/"
                    if not self.tree.exists(next_root):
                        self.tree.insert(root, tkinter.END, next_root, text=path)
                    root = next_root
                identifier = self.tree.insert(root, tkinter.END, text=project.path[last_slash + 1:])
                self.mapping[identifier] = project

    def update_items(self, _):
        self.data = configs.manifest().directory
        self.refresh_tree()


class AllProjectsTree(TreeView):
    def __init__(self, master):
        super().__init__(master)
        self.tree.heading('#0', text=locales.all_projects, anchor='w')
        eventbus.ui_listen(eventbus.TOPIC_UPDATE_MANIFEST_COMPLETE, self.update_items)
        eventbus.ui_listen(eventbus.TOPIC_SIDEBAR_SEARCH, self.refresh_tree)

    def refresh_tree(self, keyword=None):
        self.clear()
        for project in self.data:
            if keyword and keyword not in project.name:
                continue
            identifier = self.tree.insert('', tkinter.END, text=project.name)
            self.mapping[identifier] = project

    def update_items(self, _):
        self.data = configs.manifest().all_projects
        self.refresh_tree()


class GroupsTree(TreeView):
    def __init__(self, master):
        super().__init__(master)
        self.tree.heading('#0', text=locales.groups, anchor='w')
        eventbus.ui_listen(eventbus.TOPIC_UPDATE_MANIFEST_COMPLETE, self.update_items)
        eventbus.ui_listen(eventbus.TOPIC_SIDEBAR_SEARCH, self.refresh_tree)

    def refresh_tree(self, keyword=None):
        self.clear()
        for group, projects in self.data:
            self.tree.insert('', tkinter.END, group, text=group)
            for project in projects:
                if keyword and keyword not in project.name:
                    continue
                identifier = self.tree.insert(group, tkinter.END, text=project.name)
                self.mapping[identifier] = project

    def update_items(self, _):
        self.data = configs.manifest().groups.items()
        self.refresh_tree()


class Sidebar(tkinter.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.nodes = []

        self.search_input = tkinter.Entry(self)
        self.search_input.pack(side=tkinter.TOP, expand=0, fill=tkinter.X)
        self.search_input.bind('<KeyRelease>', self._update_search)

        self.notebook = ttk.Notebook(self)

        tab1 = AllProjectsTree(self.notebook)
        self.notebook.add(tab1, text=locales.all_projects)

        tab2 = DirectoryTree(self.notebook)
        self.notebook.add(tab2, text=locales.directory)

        tab3 = GroupsTree(self.notebook)
        self.notebook.add(tab3, text=locales.groups)

        self.notebook.pack(side=tkinter.TOP, expand=1, fill=tkinter.BOTH)

    def _update_search(self, _):
        search_key = self.search_input.get()
        eventbus.emit(eventbus.TOPIC_SIDEBAR_SEARCH, search_key)
