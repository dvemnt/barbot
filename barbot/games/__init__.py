# coding=utf-8

import copy

from lxml import html

from barbot import constants, utils


class Game(object):

    """Abstract game class. All games classes should contain it."""

    def __init__(self, session):
        """
        Initialization class.

        :param session: `requests.Session` instance with authentication.
        """
        self._name = None
        self._session = session
        self._page = None

        self._actions = {
            'attack': {
                'random': 'damageRandom',
                'last': 'damageLast',
            },
            'heal': {
                'random': 'healRandom',
                'last': 'healLast',
                'self': 'healSelf',
            },
            'burning': {
                'random': 'energyDamageRandom',
                'last': 'energyDamageLast',
            },
            'skills': self.get_skills_url,
        }

    def get_entry_url(self):
        """
        Get url to enter game.

        :returns: `str` url.
        """
        if self._name is None:
            raise NotImplementedError(
                'Need set `_name` or override this function.'
            )

        return utils.build_url('game/{}'.format(self._name))

    def entry(self):
        """
        Enter to game and save response.

        :returns: `lxml.html` instance.
        """
        self._session.get(constants.HOST)
        return html.fromstring(self._session.get(self.get_entry_url()).content)

    def move(self, url):
        """
        Do action (change location, attack or etc.) and save response.

        :param url: `str` url of action.
        :returns: `lxml.html` instance.
        """
        self._page = html.fromstring(self._session.get(url).content)
        return self._page

    def get_action_log(self):
        """
        Get last line from game log.

        :returns: `str` of log.
        """
        raise NotImplementedError('Need override this function.')

    def get_actions(self, actions={}):
        """
        Get available actions.

        :param actions: `dict` with actions to add or override.
        :returns: `dict` of actions.
        """
        actions = utils.update(copy.deepcopy(self._actions), actions)

        for action, types in actions.items():
            if isinstance(types, dict):
                for target, value in types.items():
                    if isinstance(value, basestring):
                        actions[action][target] = self.get_action_url(value)
                    else:
                        actions[action][target] = value()
            else:
                if isinstance(types, basestring):
                    actions[action] = self.get_action_url(types)
                else:
                    actions[action] = types()

        return actions

    def get_action_url(self, url_part):
        """
        Get action url from page by part of url.

        :param url_part: part of url.
        :returns: `str` url or `None`.
        """
        try:
            xpath = '//a[contains(@href, "{}")]/@href'.format(url_part)
            return utils.build_url(self._page.xpath(xpath)[0])
        except IndexError:
            return None

    def get_skills_url(self):
        """
        Get skills url from page.

        :returns: `list` of `str` url.
        """
        urls = self._page.xpath(
            '//a[contains(@href, "ability") '
            'and not(contains(@class, "buff"))]/@href'
        )
        return map(utils.build_url, urls)
