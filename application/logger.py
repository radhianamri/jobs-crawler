import logging
import os
from contextlib import suppress

LOG_DIR = './logs'
LOG_FILE = 'application.log'

log = logging.getLogger()

def init():
    with suppress(FileExistsError):
        os.mkdir(LOG_DIR)

    log.setLevel(logging.INFO)
    handler = logging.FileHandler(os.path.join(LOG_DIR, LOG_FILE), 'a', 'utf-8') 
    handler.setFormatter(logging.Formatter('%(asctime)-15s|%(levelname)s|%(filename)s:%(lineno)d|%(message)s'))
    log.addHandler(handler)