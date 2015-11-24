# coding=utf-8

import importlib

import configobj
from lxml import html
import requests
import randua
import dotmap

from . import utils, logger, decorators, constants


class Settings(object):

    """Class for keep settings from configuration file."""

    def __init__(self, filename):
        """
        Initialization class.

        :param filename: path to configuration file.
        """
        self._filename = filename
        self._configuration = dotmap.DotMap(self._get_from_file(filename))

    def __getattr__(self, attr):
        try:
            return self.__dict__[attr]
        except KeyError:
            return getattr(self._configuration, attr)

    @staticmethod
    def _get_from_file(filename, configspec=utils.get_configspec()):
        """
        Get settings from configuration file.

        :param filename: path to configuration file.
        :returns: `dict` of settings.
        """
        return configobj.ConfigObj(filename, configspec=configspec).dict()


class Account(object):

    """Class for actions with user data."""

    def __init__(self, username, password):
        """
        Initialization class.

        :param username: Username on barbars.ru.
        :param password: Password on barbars.ru.
        """
        self._username = username
        self._password = password

        self._session = requests.Session()
        self._session.headers.update({'User-Agent': randua.generate()})

    def authentication(self):
        """
        Authentication user on barbars.ru.

        :returns: `requests.Session` instance with authentication.
        """
        url = utils.build_url(
            'login/wicket:interface/:8:loginForm::IFormSubmitListener::'
        )
        data = {'login': self._username, 'password': self._password}

        self._session.post(url, data=data)

        return self._session

    @property
    def is_authenticated(self):
        """
        Check authentication on barbars.ru.

        :returns: `bool`.
        """
        response = self._session.get(utils.build_url('user'))
        return response.url == utils.build_url('user')


class Hero(object):

    """Class for actions with hero."""

    def __init__(self, session):
        """
        Initialization class.

        :param session: `requests.Session` instance with authentication.
        """
        self._session = session

        self._id = int(self._session.cookies['id'])
        self._name = None
        self._side = None
        self._class = None
        self._level = None

        self.hp = None  # Health points.
        self.ep = None  # Energy points.

    def _get_hero_page(self):
        """
        Get user page.

        :returns: `lxml.html` instance.
        """
        return html.fromstring(
            self._session.get(utils.build_url('user')).content
        )

    def _update_information(self):
        """
        Update information about hero.

        :returns: `bool`.
        """
        page = self._get_hero_page()

        blocks = page.xpath((
            '//*[contains(img/@src, "blue_") or contains(img/@src, "red_")]'
            '//span/text()'
        ))
        blocks = [utils.remove_spaces(block, 0) for block in blocks]

        self._name = blocks[0]
        self._level = int(blocks[1])
        self._class = blocks[2]
        self._side = blocks[3]

        return True

    def _update_status(self, page):
        """
        Get health and energy points.

        :param page: `lxml.html` instance.
        :returns: `bool`.
        """
        blocks = page.xpath('//*[contains(img/@src, "life")]/span/text()')

        self.hp = int(blocks[0])
        self.ep = int(blocks[1])

        return True

    def repair_equipment(self, check=False):
        """
        Repair all equipment.

        :param check: check instead of repair.
        :returns: `True` if need repair or repaired else `False`.
        """
        url = utils.build_url('user/body/id/{}'.format(self._id))
        response = self._session.get(url)
        page = html.fromstring(response.content)

        link = page.xpath('//a[contains(@href, "repairLink")]/@href')
        if check:
            return bool(link)

        if link:
            self._session.get(utils.build_url(link[0]))
            return True
        return False

    @property
    def is_tired(self):
        """
        Check tire of hero.

        :returns: `bool`.
        """
        page = self._get_hero_page()
        link = page.xpath('//a[contains(@href, "tire")]')

        return bool(link)


class Bot(object):

    """Bot interface class."""

    def __init__(self, filename):
        """
        Initialization class.

        :param filename: path to configuration file.
        """
        self._settings = Settings(filename)
        print(self._settings._configuration)

        self._account = Account(
            self._settings.account.username, self._settings.account.password
        )

        logger.info('Authentication...')

        self._account.authentication()
        if not self._account.is_authenticated:
            logger.info('Incorrect login or password.')
            exit()

        self._session = self._account._session

        self.hero = Hero(session=self._session)

        logger.info('Getting information about the hero...')

        self.hero._update_information()

        self._game = None

    def change_game(self, name):
        """
        Change game mode.

        Available game modes: `towers`.

        :param name: name of game mode.
        :returns: True if successfuly changed.
        """
        try:
            module = importlib.import_module('barbot.games.{}'.format(name))
            self._game = module.GAME(self._session)
        except (ImportError, AttributeError):
            logger.info('No available game named {}.'.format(name))
            exit()

    @decorators.game
    def entry(self):
        """
        Enter to current game.

        :returns: `lxml.html` instance.
        """
        return self._game.entry()

    @decorators.game
    def get_actions(self):
        """
        Get actions from current game.

        :returns: `dict` of actions.
        """
        return self._game.get_actions()

    @decorators.game
    def move(self, action):
        """
        Action in current game.

        :param action: `str` action url.
        :returns: `lxml.html` instance.
        """
        return self._game.move(action)

    @decorators.game
    def get_action_log(self):
        """
        Get last string of utils.log from current game.

        :returns: string of utils.log.
        """
        template = u'HP: {} | EP: {} | {}'
        return template.format(
            self.hero.hp, self.hero.ep, self._game.get_action_log()
        )

    def leave_game(self):
        """Leave game."""
        self._session.get(constants.HOST)
