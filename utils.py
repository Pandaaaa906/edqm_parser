# -*- coding: utf-8 -*-
from pathlib import Path

from jinja2 import Environment, select_autoescape, FileSystemLoader

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


class Document(dict):
    def __init__(self, code: str):
        super().__init__()
        self.code = code
        self['contents'] = []
        self.template = env.get_template('template.html')

    @property
    def code(self):
        return self.setdefault('code', "")

    @code.setter
    def code(self, value):
        self['code'] = value

    @property
    def title(self):
        return self.setdefault('title')

    @title.setter
    def title(self, value):
        self['title'] = value

    @property
    def contents(self):
        return self.setdefault('contents', [])

    def add_contents(self, content):
        self['contents'].append(content)

    @property
    def html(self):
        return self.template.render(**self).encode('u8')

    def render(self, root="html"):
        fname = f"{self.title}.html"
        root = Path(root)
        root.mkdir(exist_ok=True)
        fp = root / fname
        with fp.open('wb') as f:
            f.write(self.html)


class Section(dict):
    def __init__(self, subtitle):
        super().__init__()
        self.subtitle = subtitle
        self['contents'] = []

    @property
    def subtitle(self):
        return self.setdefault('subtitle')

    @subtitle.setter
    def subtitle(self, value):
        self['subtitle'] = value

    @property
    def content(self):
        return self.setdefault('contents', "")

    def add_contents(self, content):
        self['contents'].append(content)
