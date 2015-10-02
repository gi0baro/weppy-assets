# -*- coding: utf-8 -*-
"""
weppy-Assets
------------

Integrates the ``webassets`` library with Weppy, adding support for
merging, minifying and compiling CSS and Javascript files.
"""

from setuptools import setup

setup(
    name='weppy-Assets',
    version='0.3',
    url='https://github.com/gi0baro/weppy-assets',
    license='BSD',
    author='Giovanni Barillari',
    author_email='gi0baro@d4net.org',
    description='Assets management for weppy',
    long_description=__doc__,
    packages=[
        'weppy_assets',
        'weppy_assets.webassets',
        'weppy_assets.webassets.filter',
        'weppy_assets.webassets.filter.cssrewrite',
        'weppy_assets.webassets.filter.jspacker',
        'weppy_assets.webassets.filter.rjsmin'
    ],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'weppy>=0.5',
        'CoffeeScript',
        'jsmin',
        'cssmin',
        'libsass'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
