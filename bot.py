# coding=utf-8

import time
import random
import traceback

from barbot import constants, logger, barbot


def main():
    """Main function."""
    bot = barbot.Bot('barbot.conf')
    bot.change_game('towers')
    try:
        game(bot)
    except:
        print(traceback.format_exc())
        logger.info('Close bot.')
        bot.leave_game()
        exit()


def game(bot):
    """Start and contol current game."""
    logger.info('Enter to towers.')

    bot.entry()

    logger.info(u'Tower: {}'.format(bot._game._tower))

    bot.hero._update_status(bot._game._page)
    hp = bot.hero.hp

    while not bot.hero.is_tired:
        bot.hero._update_status(bot._game._page)
        actions = bot.get_actions()
        if bot.hero.hp < hp:
            if actions['move']['forward']:
                action = random.choice(actions['move']['forward'])
            elif actions['move']['backward']:
                action = random.choice(actions['move']['backward'])
            else:
                bot.entry()
                continue
        else:
            if bot.hero._class == constants.WARRIOR:
                action = choice_warrior_action(actions)
            else:
                action = choice_medic_action(actions)

            if action is None:
                bot.entry()
                continue

        bot.move(action)
        logger.info(bot.get_action_log())
        print('=' * 60)
        hp = bot.hero.hp
        time.sleep(random.randint(4, 7))


def choice_warrior_action(actions):
    """Choice the optimal action for warrior."""
    if actions['skills'] and any(actions['attack'].values()):
        action = actions['skills'][0]
    elif actions['attack']:
        if actions['attack']['tower']:
            action = actions['attack']['tower']
        elif actions['attack']['last']:
            action = actions['attack']['last']
        else:
            action = actions['attack']['random']
    elif actions['move']:
        if actions['move']['forward']:
            action = random.choice(actions['move']['forward'])
        else:
            action = random.choice(actions['move']['backward'])
    else:
        action = None

    return action


def choice_medic_action(actions):
    """Choice the optimal action for medic."""
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
            action = actions['burning']['random']
    elif actions['move']:
        if actions['move']['forward']:
            action = random.choice(actions['move']['forward'])
        else:
            action = random.choice(actions['move']['backward'])
    else:
        action = None

    return action

if __name__ == '__main__':
    main()
