import locale


class Locales:
    def __init__(self, language='simple chinese'):
        self.language = language

    @staticmethod
    def languages_list():
        return {
            'simple chinese': '简体中文',
            'english': 'English',
        }

    @property
    def title(self):
        return 'aosp-view'

    @property
    def all_projects(self):
        return {
            'simple chinese': '所有项目',
            'english': 'All Projects',
        }.get(self.language)

    @property
    def directory(self):
        return {
            'simple chinese': '目录',
            'english': 'Directory',
        }.get(self.language)

    @property
    def groups(self):
        return {
            'simple chinese': '组',
            'english': 'Groups',
        }.get(self.language)

    @property
    def preferences(self):
        return {
            'simple chinese': '首选项',
            'english': 'Preferences',
        }.get(self.language)

    @property
    def about(self):
        return {
            'simple chinese': '关于',
            'english': 'About',
        }.get(self.language)

    @property
    def info(self):
        return {
            'simple chinese': '信息',
            'english': 'Info',
        }.get(self.language)

    @property
    def help_content(self):
        return {
            'simple chinese': '这是帮助信息',
            'english': 'Help',
        }.get(self.language)

    @property
    def init_url(self):
        return {
            'simple chinese': '初始化地址',
            'english': 'Init Url',
        }.get(self.language)

    @property
    def btn_update(self):
        return {
            'simple chinese': '更新',
            'english': 'Update',
        }.get(self.language)

    @property
    def repo_path(self):
        return {
            'simple chinese': '本地路径',
            'english': 'Repo Path',
        }.get(self.language)

    @property
    def btn_setting(self):
        return {
            'simple chinese': '设置',
            'english': 'Setting',
        }.get(self.language)

    @property
    def git_path(self):
        return {
            'simple chinese': 'git路径',
            'english': 'Git Path',
        }.get(self.language)

    @property
    def ref_selector(self):
        return {
            'simple chinese': '选择分支',
            'english': 'Branch',
        }.get(self.language)

    @property
    def checkout(self):
        return {
            'simple chinese': '检出',
            'english': 'Checkout',
        }.get(self.language)

    @property
    def current_ref(self):
        return {
            'simple chinese': '当前分支',
            'english': 'Current Branch',
        }.get(self.language)

    @property
    def revision(self):
        return {
            'simple chinese': '版本',
            'english': 'Revision',
        }.get(self.language)

    @property
    def checkout_path(self):
        return {
            'simple chinese': '检出路径',
            'english': 'Checkout Path',
        }.get(self.language)

    @property
    def project(self):
        return {
            'simple chinese': '项目',
            'english': 'Project',
        }.get(self.language)


locales = Locales(
    {
        'zh_CN': 'simple chinese',
        'en_US': 'english',
    }.get(locale.getdefaultlocale()[0], 'english'))
