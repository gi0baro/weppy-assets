# -*- coding: utf-8 -*-
"""
    weppy_assets.ext
    ----------------

    Provides assets management for weppy

    :copyright: (c) 2015 by Giovanni Barillari
    :license: BSD, see LICENSE for more details.
"""

import os
from .webassets import Environment, Bundle
from weppy._compat import basestring
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
    def __init__(self, *contents, **options):
        if len(contents) == 1 and isinstance(contents[0], (list, tuple)):
            contents = contents[0]
        options['filters'] = options.get('filters') or []
        contents, options = self._initialize_(*contents, **options)
        super(Asset, self).__init__(*contents, **options)

    def _initialize_(self, *contents, **options):
        return contents, options

    def _auto_filter_(self, contents, options, exts, fname=None):
        fname = fname or exts[0]
        if fname not in options['filters']:
            counts = 0
            for el in contents:
                if isinstance(el, basestring):
                    if el.split(".")[-1] in exts:
                        counts += 1
            if counts:
                if counts != len(contents):
                    last_ext = False
                    need_filter = []
                    grouped_contents = []
                    for c in contents:
                        if isinstance(c, basestring):
                            c_ext = c.split(".")[-1]
                        else:
                            c_ext = None
                        if c_ext != last_ext:
                            grouped_contents.append([])
                            if c_ext == fname:
                                need_filter.append(True)
                            else:
                                need_filter.append(False)
                            last_ext = c_ext
                        grouped_contents[-1].append(c)
                    copt = {'filters': [fname]}
                    new_contents = []
                    for i in range(0, len(grouped_contents)):
                        if not isinstance(grouped_contents[i][0], basestring):
                            for el in grouped_contents[i]:
                                new_contents.append(el)
                        else:
                            if need_filter[i] == True:
                                new_contents.append(
                                    self.__class__(
                                        *grouped_contents[i], **copt))
                            else:
                                new_contents.append(
                                    self.__class__(*grouped_contents[i]))
                    contents = new_contents
                else:
                    options['filters'].append(fname)
        return contents, options


class JSAsset(Asset):
    def _initialize_(self, *contents, **options):
        contets, options = self._auto_filter_(contents, options, ['coffee'])
        return contents, options

    def minify(self):
        self.filters.append('jsmin')
        self._set_filters(self.filters)
        return self


class CSSAsset(Asset):
    def _initialize_(self, *contents, **options):
        contents, options = self._auto_filter_(
            contents, options, ['sass', 'scss'], 'libsass')
        return contents, options

    def minify(self):
        self.filters.append('cssmin')
        self._set_filters(self.filters)
        return self


class AssetsLexer(TemplateLexer):
    def process(self, value):
        s = '_weppy_assets_gen_("%s")' % value
        node = self.parser.create_node(s, pre_extend=False,
                                       writer_escape=False)
        self.top.append(node)


class AssetsTemplate(TemplateExtension):
    namespace = 'Assets'
    lexers = {'assets': AssetsLexer}

    def _gen_url_str(self, asset):
        urls = self.env.assets[asset].urls()
        rv = ''
        for url in urls:
            file_name = url.split("?")[0]
            file_ext = file_name.rsplit(".", 1)[-1]
            if file_ext == 'js':
                static = '<script type="text/javascript" src="' + url + \
                    '"></script>'
            elif file_ext == "css":
                static = '<link rel="stylesheet" href="' + url + \
                    '" type="text/css">'
            else:
                continue
            rv += static
        return rv

    def inject(self, context):
        context['_weppy_assets_gen_'] = self._gen_url_str
