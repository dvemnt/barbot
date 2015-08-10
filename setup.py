# -*- coding: utf-8 -*-

from os import path
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

VERSION = '1.0.1'

here = path.abspath(path.dirname(__file__))

packages = [
    'barbot'
]

with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requires = f.readlines()[1:]

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='barbot',
    version=VERSION,
    packages=packages,
    install_requires=requires,
    description='Create your bot for barbars.ru.',
    long_description=long_description,
    author='Vitalii Maslov',
    author_email='me@pyvim.com',
    url='https://github.com/pyvim/barbot',
    download_url='https://github.com/pyvim/barbot/tarball/master',
    license='MIT',
    keywords = 'barbars.ru, bot, game',
    classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
)
