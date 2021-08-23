from xml.dom import minidom


class Project:
    def __init__(self, name, path, groups):
        self.name = name
        self.path = path
        self.groups = []
        if groups:
            self.groups = groups.split(',')

    def __repr__(self):
        return f"<Project {self.name} {self.path} {','.join(self.groups)}>"


class Manifest:
    def __init__(self):
        self.content = None
        self.projects = []

    def read_xml(self):
        tree = minidom.parseString(self.content)
        document = tree.documentElement
        projects = document.getElementsByTagName("project")
        for p in projects:
            self.projects.append(Project(p.getAttribute('name'), p.getAttribute('path'), p.getAttribute('groups')))
        self.projects.sort(key=lambda x: x.name)

    def set_content(self, content):
        self.content = content
        self.projects.clear()
        self.read_xml()

    @property
    def all_projects(self):
        return self.projects

    @property
    def directory(self):
        return self.projects

    @property
    def groups(self):
        groups = {"nogroup": []}
        for project in self.projects:
            if len(project.groups) == 0:
                groups["nogroup"].append(project)
            else:
                for group in project.groups:
                    if group in groups:
                        groups[group].append(project)
                    else:
                        groups[group] = [project]
        return groups


if __name__ == "__main__":
    with open("repo/manifest-bak/default.xml", "r") as f:
        Manifest().set_content(f.read())
