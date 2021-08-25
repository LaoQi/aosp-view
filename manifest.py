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
        self.default_revision = 'master'

    def read_xml(self):
        tree = minidom.parseString(self.content)
        document = tree.documentElement
        default_ele = document.getElementsByTagName("default")[0]
        self.default_revision = default_ele.getAttribute('revision')
        if self.default_revision.startswith('refs'):
            self.default_revision = self.default_revision.split('/')[-1]

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
        groups = {"all": []}
        for project in self.projects:
            groups["all"].append(project)
            for group in project.groups:
                if group in groups:
                    groups[group].append(project)
                else:
                    groups[group] = [project]
        return groups


if __name__ == "__main__":
    with open("repo/manifest-bak/default.xml", "r") as f:
        Manifest().set_content(f.read())
