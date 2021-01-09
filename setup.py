#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

from setuptools import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_long_description():
    """
    Return the README.
    """
    return open('README.md', 'r', encoding="utf8").read()


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


setup(
    name='twbm',
    version=get_version('twbm'),
    url='https://github.com/sysid/twbm',
    license='GPLv3',
    description='bookmark manager based on buku',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='sysid',
    author_email='sysid@gmx.de',
    packages=get_packages('twbm'),
    entry_points={
        'console_scripts': ['twbm=twbm:main']
    },
    install_requires=[
        'beautifulsoup4>=4.4.1',
        'certifi',
        'cryptography>=1.2.3',
        'urllib3>=1.23',
        'html5lib>=1.0.1',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
)
