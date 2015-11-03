# coding=utf-8

import unittest

from barbot import barbot, constants
from barbot.games import towers

CONFIG_PATH = 'barbot.conf'


class SettingsTests(unittest.TestCase):

    """Testing `Settings` class."""

    def setUp(self):
        """Create testing data."""
        self.settings = barbot.Settings(CONFIG_PATH)

    def test_get_configuration(self):
        """Testing get configuration."""
        configuration = self.settings._get_configuration(CONFIG_PATH)
        self.assertIn('username', configuration['account'])
        self.assertIn('password', configuration['account'])

    def test_get_setting(self):
        """Testing get setting."""
        self.assertIsInstance(self.settings.account['username'], str)


class AccountTests(unittest.TestCase):

    """Test with Account class."""

    def setUp(self):
        """
        Create `Account` class for tests.

        Note: you must verify the existence of the configuration file and
        username and password in it to pass tests.
        """
        settings = barbot.Settings(CONFIG_PATH)
        username = settings.account['username']
        password = settings.account['password']
        self.account = barbot.Account(username, password)

    def tearDown(self):
        """Close and clear."""
        self.account._session.close()

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
        self.settings = barbot.Settings(CONFIG_PATH)
        username = self.settings.account['username']
        password = self.settings.account['password']
        account = barbot.Account(username, password)
        session = account.authentication()
        self.hero = barbot.Hero(session=session)

    def tearDown(self):
        """Close and clear."""
        self.hero._session.close()

    def test_get_information(self):
        """Test getting information about hero."""
        self.hero._update_information()
        self.assertEqual(self.hero._name, self.settings.account['username'])
        self.assertIn(self.hero._side, (constants.NORTH, constants.SOUTH))
        self.assertIn(self.hero._class, (constants.WARRIOR, constants.MEDIC))
        self.assertIsInstance(self.hero._level, int)

    def test_get_status(self):
        """Test getting health and energy points."""
        self.hero._update_status(self.hero._get_hero_page())
        self.assertIsInstance(self.hero.hp, int)
        self.assertIsInstance(self.hero.ep, int)

    def test_repair_equipment(self):
        """Test repair equipment."""
        self.hero.repair_equipment()
        self.assertFalse(self.hero.repair_equipment(check=True))

    def test_is_tired(self):
        """Test checking tire of hero."""
        self.assertIsInstance(self.hero.is_tired, bool)


class TowersTests(unittest.TestCase):

    """Tests for Tower class."""

    def setUp(self):
        """
        Create `Hero` class for tests.

        Note: you must verify the existence of the configuration file and
        username and password in it to pass tests.
        """
        self.settings = barbot.Settings(CONFIG_PATH)
        username = self.settings.account['username']
        password = self.settings.account['password']
        account = barbot.Account(username, password)
        session = account.authentication()
        self.towers = towers.Towers(session=session)

    def tearDown(self):
        """Close and clear."""
        self.towers._session.get(constants.HOST)  # leave battle
        self.towers._session.close()

    def test_entry(self):
        """Test getting information for towers game mode."""
        self.towers.entry()
        self.assertIsInstance(self.towers._capital, basestring)
        self.assertIsInstance(self.towers._tower, basestring)

    def test_move(self):
        """Test tower actions."""
        self.towers.entry()
        self.assertNotEqual(self.towers._page, None)

    def test_get_actions(self):
        """Test getting actions in towers."""
        self.towers.entry()
        self.assertIsInstance(self.towers.get_actions(), dict)

if __name__ == '__main__':
    unittest.main()
