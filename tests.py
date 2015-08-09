# -*- coding: utf-8 -*-

import unittest
import time

import configobj

import barbot
from barbot.constants import HOST
from barbot.exceptions import ConfigurationError

CONFIG = configobj.ConfigObj('barbot.conf')


class AccountTests(unittest.TestCase):

    """Test with Account class."""

    def setUp(self):
        """
        Create `Account` class for tests.

        Note: you must verify the existence of the configuration file and
        username and password in it to pass tests.
        """
        self.account = barbot.Account(config=CONFIG)

    def tearDown(self):
        """Close and clear."""
        self.account.session.close()

    def test_init(self):
        """Test `Account` class initialization."""
        username, password = 'username', 'password'
        self.assertRaises(ConfigurationError, barbot.Account)
        self.assertRaises(ConfigurationError, barbot.Account, config=set())
        self.assertRaises(ConfigurationError, barbot.Account, config=dict())
        config = {'account': ''}
        self.assertRaises(ConfigurationError, barbot.Account, config=config)
        config = {'account': {'username': username}}
        self.assertRaises(ConfigurationError, barbot.Account, config=config)
        config = {'account': {'password': password}}
        self.assertRaises(ConfigurationError, barbot.Account, config=config)

        config = {'account': {'username': username, 'password': password}}
        account = barbot.Account(config=config)
        self.assertEqual(account._username, username)
        self.assertEqual(account._password, password)

    def test_authentication(self):
        """
        Test authentication.

        Note: you must put valid username and password into configuration file.
        """
        self.account.authentication()
        self.assertEqual(self.account.is_authenticated, True)


class HeroTests(unittest.TestCase):

    """Test for Hero class."""

    def setUp(self):
        """
        Create `Hero` class for tests.

        Note: you must verify the existence of the configuration file and
        username and password in it to pass tests.
        """
        account = barbot.Account(config=CONFIG)
        session = account.authentication()
        self.hero = barbot.Hero(session=session)

    def tearDown(self):
        """Close and clear."""
        self.hero.session.close()

    def test_init(self):
        """Test `Hero` class initialization."""
        account = barbot.Account(config=CONFIG)
        session = account.authentication()
        hero = barbot.Hero(session=session)
        hero.session.close()
        self.assertIsInstance(hero._id, int)

    def test_get_information(self):
        """Test getting information about hero."""
        self.hero.get_information()
        self.assertEqual(self.hero._name, CONFIG['account']['username'])
        self.assertIn(self.hero._side, ('север', 'юг'))
        self.assertIn(self.hero._spec, ('воин', 'медик'))
        self.assertIsInstance(self.hero._level, int)

    def test_get_status(self):
        """Test getting health and energy points."""
        self.hero.get_status(self.hero.session.get('http://barbars.ru/user'))
        self.assertIsInstance(self.hero.hp, int)
        self.assertIsInstance(self.hero.ep, int)

    def test_repair_equipment(self):
        """Test repair equipment."""
        self.hero.repair_equipment()
        self.assertFalse(self.hero.repair_equipment(check=True))

    def test_get_tire(self):
        """Test checking tire of hero."""
        self.assertIsInstance(self.hero.check_tire(), bool)


class TowerTests(unittest.TestCase):

    """Tests for Tower class."""

    def setUp(self):
        """
        Create `Hero` class for tests.

        Note: you must verify the existence of the configuration file and
        username and password in it to pass tests.
        """
        account = barbot.Account(config=CONFIG)
        session = account.authentication()
        self.towers = barbot.Towers(session=session)

    def tearDown(self):
        """Close and clear."""
        self.towers.session.get(HOST)  # leave battle
        self.towers.session.close()

    def test_entry(self):
        """Test getting information for towers game mode."""
        self.towers.entry()
        self.assertIsInstance(self.towers._capital, str)
        self.assertIsInstance(self.towers.tower, str)
        self.assertEqual(self.towers.tower, self.towers.location)

    def test_move(self):
        """Test tower actions."""
        response = self.towers.response
        self.assertNotEqual(self.towers.entry(), response)

    def test_get_actions(self):
        """Test getting actions in towers."""
        self.towers.entry()
        self.assertIsInstance(self.towers.get_actions(), dict)

    def test_get_log(self):
        """Test getting log."""
        self.towers.entry()
        if not self.towers.get_actions()['skills']:
            time.sleep(25)
            self.towers.entry()
        self.towers.move(self.towers.get_actions()['skills'][0])
        self.assertIsInstance(self.towers.get_log(), str)

    def test_return_to_capital(self):
        """Test return to the capital."""
        self.towers.entry()
        self.towers.move(self.towers.get_actions()['move']['forward'][0])
        self.towers.return_to_capital()
        self.assertEqual(self.towers.location, self.towers._capital)


class InterfaceTests(unittest.TestCase):

    """Tests for Interface class."""

    def setUp(self):
        """Create `Interface` class for tests."""
        self.interface = barbot.Interface(config=CONFIG)

    def tearDown(self):
        """Close and clear."""
        self.interface._session.close()

    def test_change_game(self):
        """Test change game."""
        self.interface.change_game('towers')
        self.assertEqual(self.interface.game, self.interface.towers)

    def test_entry(self):
        """Test entry to current game."""
        self.interface.change_game('towers')
        self.interface.entry()
        self.assertIsNotNone(self.interface.towers.response)

    def test_get_actions(self):
        """Test get actions in current game."""
        self.interface.change_game('towers')
        self.interface.entry()
        self.assertIsInstance(self.interface.get_actions(), dict)

    def test_move(self):
        """Test move in current game."""
        self.interface.change_game('towers')
        self.interface.entry()
        response = self.interface.towers.response
        self.interface.move(self.interface.get_actions()['move']['forward'][0])
        self.assertNotEqual(self.interface.towers.response, response)

    def test_get_log(self):
        """Test getting log from current game."""
        self.interface.change_game('towers')
        self.interface.entry()
        if not self.interface.get_actions()['skills']:
            time.sleep(20)
            self.interface.entry()
        self.interface.move(self.interface.get_actions()['skills'][0])
        self.assertIsInstance(self.interface.get_log(), str)

if __name__ == '__main__':
    unittest.main()
