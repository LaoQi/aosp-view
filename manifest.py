from xml.dom import minidom

import configs


class Remote:
    def __init__(self, name, fetch):
        # remove review: not support upload
        # self.alias = alias  # not support alias
        self.name = name
        self.fetch = fetch


class Project:
    def __init__(self, name, path, revision, remote, groups):
        # always clone-depth="1"
        self.name = name
        self.path = path
        if path == '':
            self.path = name
        self.revision = revision
        self.remote = remote
        self.groups = []
        if groups:
            self.groups = groups.split(',')

    def __repr__(self):
        return f"<Project {self.name} {self.path} {self.revision} {self.remote} {','.join(self.groups)}>"

    @property
    def url(self):
        name = self.name
        if not name.endswith(".git"):
            name = f"{self.name}.git"
        if self.remote.fetch == '..':
            return f"{'/'.join(configs.init_url().split('/')[:-2])}/{name}"
        return f"{self.remote.fetch}/{name}"


def _default_attr(node, key, default=''):
    value = node.getAttribute(key)
    if not value or len(value) == 0:
        return default
    return value


class Manifest:
    def __init__(self):
        self.content = None
        self.projects = []
        self.default_revision = 'master'
        self.default_remote_name = ''

    def read_xml(self):
        tree = minidom.parseString(self.content)
        document = tree.documentElement

        remotes = {}

        remote_elements = document.getElementsByTagName('remote')
        for ele in remote_elements:
            remotes[ele.getAttribute('name')] = Remote(
                ele.getAttribute('name'), _default_attr(ele, 'fetch', ''))

        default_ele = document.getElementsByTagName("default")[0]
        self.default_revision = default_ele.getAttribute('revision')
        if self.default_revision.startswith('refs'):
            self.default_revision = self.default_revision.split('/')[-1]

        self.default_remote_name = default_ele.getAttribute('remote')

        project_elements = document.getElementsByTagName("project")
        for p in project_elements:
            remote_name = _default_attr(p, 'remote', self.default_remote_name)
            revision = _default_attr(p, 'revision', self.default_revision)
            upstream = _default_attr(p, 'upstream')
            if upstream:
                # ignore revision
                revision = upstream
            self.projects.append(
                Project(
                    name=_default_attr(p, 'name'), path=_default_attr(p, 'path'),
                    revision=revision,
                    remote=remotes.get(remote_name),
                    groups=_default_attr(p, 'groups')))
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
        groups = {"ungrouped": []}
        for project in self.projects:
            if len(project.groups) == 0:
                groups["ungrouped"].append(project)
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
