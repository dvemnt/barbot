# Barbot #
*Create your bot for [barbars.ru](http://barbars.ru)*

## Installation ##
```bash
pip install barbot
```

## Configuration ##
Syntax of [barbot.conf](https://github.com/pyvim/barbot/blob/master/barbot.conf)
```
[account]
username = YOUR-USERNAME
password = YOUR-PASSWORD
```

## Usage ##
```python
from barbot import barbot

bot = barbot.Bot('barbot.conf')  # configuration.
bot.change_game('towers')  # change game to 'towers'.
bot.entry()  # enter to game.
actions = bot.get_actions()  # get available actions.
bot.move(actions['attack']['tower'])  # attack enemy tower.
```

Also see [example bot](https://github.com/pyvim/barbot/blob/master/bot.py).

## Documentation ##
In development. See docstrings.

## Tests ##
Before run tests you need add valid username and password to [barbot.conf](https://github.com/pyvim/barbot/blob/master/barbot.conf).
```bash
nosetests -v
```
or
```bash
python tests.py
```

## Changelog ##
See [CHANGELOG.md](https://github.com/pyvim/barbot/blob/master/CHANGELOG.md)

## License ##
See [LICENSE](https://github.com/pyvim/barbot/blob/master/LICENSE)
