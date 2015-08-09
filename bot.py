# -*- coding: utf-8 -*-

import time
import random
import traceback

import barbot
from barbot.utils import log, battle_log
from barbot.constants import HOST


def main():
    """Main function."""
    bot = barbot.Interface('barbot.conf')
    bot.change_game('tower')
    try:
        game(bot)
    except:
        print(traceback.format_exc())
        log('Close bot.')
        bot._session.get(HOST)  # leave battle
        exit


def game(bot):
    """Start and contol current game."""
    log('Enter to towers...')
    bot.entry()
    log('Tower: {}'.format(bot.game.tower))
    bot.hero.get_status(bot.game.response)
    hp = bot.hero.hp
    while bot.hero.check_tire:
        bot.hero.get_status(bot.game.response)
        actions = bot.get_actions()
        if bot.hero.hp < hp:
            if actions['move']['forward']:
                action = random.choice(actions['move']['forward'])
            elif actions['move']['backward']:
                action = random.choice(actions['move']['backward'])
            else:
                bot.entry()
                continue
        elif bot.hero.hp <= 1000:
            log('Low health. Return to capital for resting...')
            bot.game.return_to_capital()
            time.sleep(25)
            bot.entry()
            continue
        else:
            action = choice_action(actions)
            if action is None:
                bot.entry()
                continue
        time.sleep(random.randint(4, 7))
        bot.move(action)
        battle_log(bot)
        print('=' * 60)
        hp = bot.hero.hp


def choice_action(actions):
    """Choice the optimal action."""
    action = None

    if actions['skills'] and any(actions['attack'].values()):
        action = actions['skills'][0]
    elif actions['attack']:
        if actions['attack']['tower']:
            action = actions['attack']['tower']
        elif actions['attack']['last']:
            action = actions['attack']['last']
        else:
            action = actions['attack']['new']
    elif actions['move']:
        if actions['move']['forward']:
            action = random.choice(actions['move']['forward'])
        else:
            action = random.choice(actions['move']['backward'])

    return action

if __name__ == '__main__':
    main()
