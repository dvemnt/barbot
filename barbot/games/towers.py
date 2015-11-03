# coding=utf-8

from barbot import games, utils


class Towers(games.Game):

    """Towers game."""

    def __init__(self, session):
        """
        Initialization class.

        :param session: `requests.Session` instance with authentication.
        """
        super(Towers, self).__init__(session)

        self._name = 'towers'
        self._capital = None
        self._tower = None
        self._location = None

    def entry(self):
        """
        Enter to game.

        :returns: `str` url for entry to game.
        """
        page = super(Towers, self).entry()

        self._capital = utils.remove_spaces(page.xpath('//h1//text()')[0])

        tower_link = page.xpath('//a[contains(@href, "nearLocation")]')[0]
        self._tower = utils.remove_spaces(tower_link.xpath('span/text()')[0])
        self._location = self._tower

        return self.move(utils.build_url(tower_link.xpath('@href')[0]))

    def move(self, url):
        """
        Do action (change location, attack or etc.) and save response.

        :param url: `str` url of action.
        :returns: `lxml.html` instance.
        """
        page = super(Towers, self).move(url)
        self._location = utils.remove_spaces(page.xpath('//h1/span/text()')[0])
        return page

    def get_action_log(self):
        """
        Get last line from game log.

        :returns: `str` of log.
        """
        log = self._page.xpath(u'//div[contains(text(), "Ты")][1]//text()')
        return u'Location: {}\n{}'.format(
            self._location, utils.remove_spaces(''.join(log))
        )

    def get_actions(self):
        """
        Get available actions.

        :returns: dict of actions.
        {
            'attack': {
                'random': url or `None`,
                'last': url or `None`,
                'tower': url or `None`,
            },
            'heal': {
                'random': url or `None`,
                'last': url or `None`,
                'self': url or `None`,
            },
            'burning': {
                'random': url or `None`,
                'last': url or `None`,
            },
            'skills': [urls],
            'move': {
                'backward': [urls],
                'forward': [urls],
                'capital': url or `None`,
            },
        }
        """
        actions = {
            'attack': {
                'tower': 'damageTower',
            },
            'move': {
                'backward': self.get_move_backward_urls,
                'forward': self.get_move_forward_urls,
                'capital': self.get_move_capital_url,
            },
        }

        return super(Towers, self).get_actions(actions)

    def get_move_backward_urls(self):
        """
        Get backward towers url from page.

        :returns: `list` of `str` url.
        """
        urls = self._page.xpath('//a[contains(@href, "location")]')

        if '-n' in urls[0].xpath('img/@src')[0]:
            backward = '-n'
        elif '-s' in urls[0].xpath('img/@src')[0]:
            backward = '-s'
        else:
            return []

        urls = filter(lambda x: backward in x.xpath('img/@src')[0], urls)
        return map(lambda x: utils.build_url(x.xpath('@href')[0]), urls)

    def get_move_forward_urls(self):
        """
        Get backward towers url from page.

        :returns: `list` of `str` url.
        """
        urls = self._page.xpath('//a[contains(@href, "location")]')

        if '-n' in urls[-1].xpath('img/@src')[0]:
            forward = '-n'
        elif '-s' in urls[-1].xpath('img/@src')[0]:
            forward = '-s'
        else:
            return []

        urls = filter(lambda x: forward in x.xpath('img/@src')[0], urls)
        return map(lambda x: utils.build_url(x.xpath('@href')[0]), urls)

    def get_move_capital_url(self):
        """
        Get capital url from page.

        :returns: `str` url or `None`.
        """
        urls = self._page.xpath('//a[contains(@href, "location")]')

        condition = lambda x: (
            utils.remove_spaces(x.xpath('span/text()')[0]) == self._capital
        )

        try:
            return filter(condition, urls)[0]
        except IndexError:
            return None

GAME = Towers
