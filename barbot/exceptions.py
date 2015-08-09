# -*- coding: utf-8 -*-


class AuthenticationError(Exception):

    """Exception for errors with authentication."""

    pass


class GameError(Exception):

    """Exception for errors with different games."""

    pass


class ConfigurationError(Exception):

    """Exception for errors with setup and configuration."""

    pass
