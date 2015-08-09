# -*- coding: utf-8 -*-

import configobj
from lxml import html
import requests
from fake_useragent import UserAgent

from .utils import clean, build_url, log
from .constants import HOST
from .exceptions import (
    AuthenticationError, GameError, ConfigurationError
)


class Account(object):

    """Class for actions with user data."""

    def __init__(self, config=None):
        """
        Initialization class.

        :param username: Username on barbars.ru.
        :param password: Password on barbars.ru.
        :param config: dictionary with authentication parameters.
        """
        try:
            self._config = config
            self._username = self._config['account']['username']
            self._password = self._config['account']['password']
        except:
            raise ConfigurationError('Not username or password.')

        self.is_authenticated = False
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': UserAgent().random})

    def authentication(self):
        """
        Authentication user on barbars.ru.

        :returns: `requests` Session class with authentication or `False`.
        """
        url = build_url(
            'login/wicket:interface/:7:loginForm::IFormSubmitListener::')
        data = {'login': self._username, 'password': self._password}

        response = self.session.post(url, data=data)
        if response.status_code == 404:  # Yes, it's strange.
            self.is_authenticated = True
            return self.session
        return False


class Hero(object):

    """Class for actions with hero."""

    def __init__(self, session):
        """
        Initialization class.

        :param session: `requests` Session class with authentication.
        """
        self.session = session

        self._id = int(self.session.cookies['id'])
        self._name = None
        self._side = None
        self._spec = None
        self._level = None

        self.hp = None  # Health points.
        self.ep = None  # Energy points.

        self.captcha = None
        self.tire = None

    def get_user_page(self):
        """
        Get user page.

        :returns: `requests` response.
        """
        return self.session.get(build_url('user'))

    def get_information(self):
        """
        Get information about hero.

        :returns: `True` or `False` if have problems.
        """
        response = self.get_user_page()
        page = html.fromstring(response.content)

        blocks = page.xpath(
            '//*[contains(img/@src, "blue_") or contains(img/@src, "red_")] \
            //span/text()')
        blocks = [clean(block, 0) for block in blocks]
        try:
            self._name = blocks[0]
            self._level = int(blocks[1])
            self._spec = blocks[2]
            self._side = blocks[3]
        except:
            return False
        return True

    def get_status(self, response):
        """
        Get health and energy points.

        :param response: `requests` response.
        :returns: bool.
        """
        page = html.fromstring(response.content)
        blocks = page.xpath('//*[contains(img/@src, "life")]/span/text()')
        try:
            self.hp = int(blocks[0])
            self.ep = int(blocks[1])
        except:
            return False
        return True

    def repair_equipment(self, check=False):
        """
        Repair all equipment.

        :param check: check instead of repair.
        :returns: `True` if need repair or repaired else `False`.
        """
        url = build_url('user/body/id/{}'.format(self._id))
        response = self.session.get(url)
        page = html.fromstring(response.content)

        link = page.xpath('//a[contains(@href, "repairLink")]/@href')
        if check:
            return bool(link)

        if link:
            self.session.get(build_url(link[0]))
            return True
        return False

    def check_tire(self):
        """
        Check tire of hero.

        :returns: bool.
        """
        response = self.get_user_page()
        page = html.fromstring(response.content)
        link = page.xpath('//a[contains(@href, "tire")]')
        if not link:
            return False
        return True


class AbstractGame(object):

    """
    Abstract game class.

    Class comprises a set of basic functions to connect to a common interface.
    """

    def __init__(self, session):
        """
        Initialization class.

        :param session: `requests` Session class with authentication.
        """
        self._session = session
        self.response = None

    def entry(self):
        """
        Enter to game.

        :returns: url for entry.
        """
        raise NotImplementedError('Need override this function.')

    def get_actions(self):
        """
        Get available actions.

        :returns: dict of actions.
        """
        raise NotImplementedError('Need override this function.')

    def move(self, url):
        """
        Change location or attack and save response.

        :returns: response.
        """
        raise NotImplementedError('Need override this function.')

    def get_log(self):
        """
        Getting last line from log with hero action.

        :returns: string of log.
        """
        raise NotImplementedError('Need override this function.')


class Towers(AbstractGame):

    """Towers game."""

    def __init__(self, session):
        """
        Initialization class.

        :param session: `requests` Session class with authentication.
        """
        self.session = session
        self.response = None

        self._capital = None
        self.tower = None
        self.location = None

    def entry(self):
        """
        Enter to tower.

        :returns: `requests` response.
        """
        self.session.get(HOST)
        response = self.session.get(build_url('game/towers'))
        page = html.fromstring(response.content)

        self._capital = clean(page.xpath('//h1/span/text()')[0])
        tower_link = page.xpath('//a[contains(@href, "nearLocation")]')[0]
        self.tower = clean(tower_link.xpath('span/text()')[0])

        return self.move(build_url(tower_link.xpath('@href')[0]))

    def move(self, url):
        """
        Change location or attack and save response.

        :returns: response.
        """
        self.response = self.session.get(url)
        page = html.fromstring(self.response.content)
        self.location = clean(page.xpath('//h1/span/text()')[0])
        return self.response

    def get_actions(self):
        """
        Get available actions.

        :returns: dict of actions.
        {
            'attack': {
                'new': url or False, # attack new enemy.
                'last': url or False, # attack last enemy.
                'tower': url or False, # attack tower.
            }
            'skills': [urls], # list urls of available skills.
            'move': {
                'backward': [urls],
                'forward': [urls],
            }
        }
        """
        # TODO: medic actions.

        actions = {
            'attack': {},
            'skills': [],
            'move': {
                'backward': [],
                'forward': [],
                'capital': False,
            },
        }
        page = html.fromstring(self.response.content)

        link = page.xpath('//a[contains(@href, "damageRandomEnemy")]/@href')
        actions['attack']['new'] = build_url(link[0]) if link else False

        link = page.xpath('//a[contains(@href, "damageLastTarget")]/@href')
        actions['attack']['last'] = build_url(link[0]) if link else False

        link = page.xpath('//a[contains(@href, "damageTower")]/@href')
        actions['attack']['tower'] = build_url(link[0]) if link else False

        links = page.xpath(
            '//a[contains(@href, "ability") '
            'and not(contains(@class, "buff"))]/@href')
        actions['skills'] = [build_url(skill_link) for skill_link in links]

        links = page.xpath('//a[contains(@href, "location")]')
        if '-n' in links[0].xpath('img/@src')[0]:
            backward = '-n'
        elif '-s' in links[0].xpath('img/@src')[0]:
            backward = '-s'
        for link in links:
            if clean(link.xpath('span/text()')[0]) == self._capital:
                actions['move']['capital'] = build_url(link.xpath('@href')[0])
                continue
            href = link.xpath('@href')[0]
            if backward in link.xpath('img/@src')[0]:
                actions['move']['backward'].append(build_url(href))
            else:
                actions['move']['forward'].append(build_url(href))
        return actions

    def get_log(self):
        """
        Getting last line from game log.

        :returns: string of log.
        """
        page = html.fromstring(self.response.content)
        log = page.xpath('//div[contains(text(), "Ты")][1]//text()')
        return clean(''.join(log))

    def return_to_capital(self, force=False):
        """
        Return hero to the capital.

        :param force: force return to the capital with exit from towers.
        :returns: bool result.
        """
        if force:
            self.session.get(HOST)
            self.move(build_url('game/towers'))
            return True

        while self.location != self._capital:
            actions = self.get_actions()
            try:
                if not actions['move']['capital']:
                    self.move(actions['move']['backward'][0])
                else:
                    self.move(actions['move']['capital'])
            except:
                return False
        return True


class Interface(object):

    """Wrapper for units."""

    def __init__(self, config=None):
        """
        Initialization interface and need class.

        :param config: path to configuration file.
        """
        if config is None:
            raise ConfigurationError('Need path to configuration file.')
        self._config = configobj.ConfigObj(config)

        self.account = Account(config=self._config)
        log('Authentication...')
        if not self.account.authentication():
            raise AuthenticationError('Incorrect login or password.')
        self._session = self.account.session

        self.hero = Hero(session=self._session)
        log('Getting information about the hero...')
        if not self.hero.get_information():
            raise ConfigurationError('Impossible get information about hero.')

        self.towers = Towers(session=self._session)

        self._game = None

        log('Ready to game.')

    def change_game(self, game):
        """
        Change game mode.

        Available game modes: `tower`.

        :param game: name of game mode.
        :returns: True if successfuly changed.
        """
        if getattr(self, game, None) is not None:
            self._game = game
            return True
        raise GameError('No available game with such name.')

    @property
    def game(self):
        """
        Get current game.

        :returns: game class or None.
        """
        return getattr(self, self._game, None)

    def entry(self):
        """
        Enter to current game.

        :returns: url to enter in game.
        """
        if self.game is None:
            raise GameError('No current game.')
        return self.game.entry()

    def get_actions(self):
        """
        Get actions in current game.

        :returns: dict of actions.
        """
        if self.game is None:
            raise GameError('No current game.')
        return self.game.get_actions()

    def move(self, action):
        """
        Action in current game.

        :param action: action url.
        :returns: `requests` response.
        """
        if self.game is None:
            raise GameError('No current game.')
        return self.game.move(action)

    def get_log(self):
        """
        Get last string of log from current game.

        :returns: string of log.
        """
        if self.game is None:
            raise GameError('No current game.')
        return self.game.get_log()
