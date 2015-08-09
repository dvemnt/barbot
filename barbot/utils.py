"""Utils module."""

# -*- coding: utf-8 -*-

import re
import time

import configobj
import urltools

from .constants import HOST


def config_generator(filename='barbot.conf'):
    """
    Create configuration template.

    :param filename: path to created configuration.
    """
    config = configobj.ConfigObj()
    config.filename = filename

    # Authentication data.
    config['account'] = {}
    config['account']['username'] = 'YOUR-USERNAME'
    config['account']['password'] = 'YOUR-PASSWORD'

    # TODO: Other blocks for different game modes.

    config.write()


def clean(string, spaces=1):
    """
    Delete extra spaces from srting.

    :param spaces: count of extra spaces to save.
    """
    return re.sub('\s+', ' ' * spaces, string).rstrip().lstrip()


def build_url(link):
    """Create valid URL from link."""
    return urltools.normalize(''.join((HOST, link)))


def log(message):
    """
    Print log.

    :param message: message for print.
    """
    print('[{}] {}'.format(time.strftime('%H:%M:%S'), str(message)))


def battle_log(bot):
    """
    Print log with battle parameters.

    :param bot: `Interface` class.
    """
    game = bot.game
    print('[{}] HP: {} | MP: {} | Location: {}\n{}'.format(
        time.strftime('%H:%M:%S'), bot.hero.hp, bot.hero.ep,
        game.location, game.get_log()))
