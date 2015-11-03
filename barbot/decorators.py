# coding=utf-8


def game(function):
    """Decorator for check available game in attribute named `_game`."""
    def _decorator(self, *args, **kwargs):
        if self._game is None:
            raise RuntimeError('Not chosen game.')
        return function(self, *args, **kwargs)
    return _decorator
