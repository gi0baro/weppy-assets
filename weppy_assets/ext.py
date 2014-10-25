# -*- coding: utf-8 -*-
"""
    weppy_assets.ext
    ----------------

    Provides assets management for weppy

    :copyright: (c) 2014 by Giovanni Barillari
    :license: BSD, see LICENSE for more details.
"""

import os
from .webassets import Environment, Bundle
from weppy.extensions import Extension, TemplateExtension, TemplateLexer


class Assets(Extension):
    default_config = dict(
        out_folder='gen'
    )

    def _load_config(self):
        self.config.out_folder = self.config.get(
            'out_folder', self.default_config['out_folder'])

    def on_load(self):
        self._load_config()
        assets_path = os.path.join(self.app.root_path, "assets")
        if not os.path.exists(assets_path):
            os.mkdir(assets_path)
        out_path = os.path.join(self.app.static_path, self.config.out_folder)
        out_url = '/static'+((self.config.out_folder and
                             '/'+self.config.out_folder) or '')
        self._assets = Environment(out_path, out_url, load_path=[assets_path])
        self.app.add_template_extension(AssetsTemplate)
        self.env.assets = self._assets

    @property
    def register(self):
        return self._assets.register

    @property
    def css(self):
        return CSSAsset

    @property
    def js(self):
        return JSAsset


class Asset(Bundle):
    def __init__(self, contents, **options):
        if not isinstance(contents, (list, tuple)):
            contents = [contents]
        options['filters'] = options.get('filters') or []
        super(Asset, self).__init__(*contents, **options)


class JSAsset(Asset):
    def __init__(self, contents, **options):
        if not isinstance(contents, (list, tuple)):
            contents = [contents]
        options['filters'] = options.get('filters') or []
        # auto-filtering coffee assets
        coffees = []
        for el in contents:
            if isinstance(el, basestring):
                if el.split(".")[-1] == "coffee":
                    coffees.append(el)
        if coffees and not 'coffee' in options['filters']:
            if coffees != contents:
                nocoffee = [c for c in contents if c not in coffees]
                copt = {'filters': ['coffee']}
                contents = [JSAsset(coffees, **copt),
                            JSAsset(nocoffee)]
            else:
                options['filters'].append('coffee')
        super(JSAsset, self).__init__(contents, **options)

    def minify(self):
        self.filters.append('jsmin')
        self._set_filters(self.filters)
        return self


class CSSAsset(Asset):
    def __init__(self, contents, **options):
        if not isinstance(contents, (list, tuple)):
            contents = [contents]
        options['filters'] = options.get('filters') or []
        # auto-filtering sass assets
        _ext = ['sass', 'scss']
        sass = []
        for el in contents:
            if isinstance(el, basestring):
                if el.split(".")[-1] in _ext:
                    sass.append(el)
        if sass and not 'libsass' in options['filters']:
            if sass != contents:
                nosass = [c for c in contents if c not in sass]
                copt = {'filters': ['libsass']}
                contents = [CSSAsset(sass, **copt),
                            CSSAsset(nosass)]
            else:
                options['filters'].append('libsass')
        super(CSSAsset, self).__init__(contents, **options)

    def minify(self):
        self.filters.append('cssmin')
        self._set_filters(self.filters)
        return self


class AssetsLexer(TemplateLexer):
    def process(self, value, top, stack):
        urls = self.ext.env.assets[value].urls()
        for url in urls:
            file_name = url.split("?")[0]
            file_ext = file_name.rsplit(".", 1)[-1]
            if file_ext == 'js':
                static = '<script type="text/javascript" src="'+url+'"></script>'
            elif file_ext == "css":
                static = '<link rel="stylesheet" href="'+url+'" type="text/css">'
            else:
                continue
            node = self.parser.create_htmlnode(static, pre_extend=False)
            top.append(node)


class AssetsTemplate(TemplateExtension):
    namespace = 'Assets'
    lexers = {'assets': AssetsLexer}
