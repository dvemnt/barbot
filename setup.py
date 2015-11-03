# coding=utf-8

from os import path
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

VERSION = '1.2.1'

here = path.abspath(path.dirname(__file__))

packages = [
    'barbot'
]

requires = [
    'configobj',
    'lxml',
    'nose',
    'randua',
    'requests'
]

with open(path.join(here, 'README.rst')) as f:
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
    keywords='barbars.ru, bot, game',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
)
