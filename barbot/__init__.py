# coding=utf-8

import logging

logging.basicConfig(
    level=logging.INFO, format='[%(asctime)s]: %(message)s',
    datefmt='%d.%m.%Y %I:%M:%S'
)
logging.getLogger('requests').setLevel(logging.CRITICAL)
logger = logging.getLogger()
