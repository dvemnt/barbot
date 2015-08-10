# -*- coding: utf-8 -*-

import time
import random
import traceback

import barbot
from barbot.utils import log, battle_log
from barbot.constants import HOST, WARRIOR, MEDIC


def main():
    """Main function."""
    bot = barbot.Interface('barbot.conf')
    bot.change_game('towers')
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
            bot.move(bot.get_actions()['move']['foreward'][0])
            continue
        else:
            if bot.hero._spec == WARRIOR:
                action = choice_warrior_action(actions)
            else:
                action = choice_medic_action(actions)
            if action is None:
                bot.entry()
                continue
        time.sleep(random.randint(4, 7))
        bot.move(action)
        battle_log(bot)
        print('=' * 60)
        hp = bot.hero.hp


def choice_warrior_action(actions):
    """Choice the optimal action for warrior."""
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
    else:
        bot.entry()

    return action

def choice_medic_action(actions):
    """Choice the optimal action for medic."""
    action = None

    if actions['heal']:
        if actions['heal']['self']:
            action = actions['heal']['self']
        elif actions['heal']['last']:
            action = actions['heal']['last']
        else:
            action = actions['heal']['new']
    elif actions['skills'] and any(actions['burning'].values()):
        action = actions['skills'][0]
    elif actions['burning']:
        if actions['burning']['last']:
            action = actions['burning']['last']
        else:
            action = actions['burning']['new']
    elif actions['move']:
        if actions['move']['forward']:
            action = random.choice(actions['move']['forward'])
        else:
            action = random.choice(actions['move']['backward'])
    else:
        bot.entry()

    return action

if __name__ == '__main__':
    main()
