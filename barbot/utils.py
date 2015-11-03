# coding=utf-8

import re

import configobj
import urltools

from . import constants


def config_generator(filename='barbot.conf'):
    """
    Create configuration template.

    :param filename: path to write configuration.
    """
    config = configobj.ConfigObj()
    config.filename = filename

    config['account'] = {}
    config['account']['username'] = 'YOUR-USERNAME'
    config['account']['password'] = 'YOUR-PASSWORD'

    config.write()


def remove_spaces(string, spaces=1):
    """
    Delete extra spaces from srting.

    :param string: `str` for remove spaces.
    :param spaces (optional): `int` count of extra spaces to save.
    :returns: `str` cleaned string.
    """
    return re.sub('\s+', ' ' * spaces, string).rstrip().lstrip()


def build_url(link):
    """
    Create valid URL from link.

    :param link: `str` relative url.
    :returns: `str` absolute url.
    """
    return urltools.normalize(''.join((constants.HOST, link)))


def update(current, new):
    """
    Recursively merge or update dictionaries.

    :rapam current: `dict` for update.
    :param new: `dict` updater.
    :returns: updated `dict`.
    """
    for key, value in new.items():
        if isinstance(value, dict):
            result = update(current.get(key, {}), value)
            current[key] = result
        elif new[key] is not None:
            current[key] = new[key]
    return current
