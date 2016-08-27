#!/usr/bin/env python3.5
"""The main module"""

import json
import getopt
import sys
import time
from os.path import realpath
import constants
import shelve
import telegram_sender
import vk_fetcher
import logging

help_message = 'vk_to_telegram.py config.json'


def _read_config(config_file):
    config_json = json.loads(open(config_file).read())

    public_walls = config_json['public_walls'] if 'public_walls' in config_json else None
    private_walls = config_json['private_walls'] if 'private_walls' in config_json else None
    bot_token = config_json['telegram_bot_token']
    user_ids = config_json['user_ids']
    access_token = config_json['vk_access_token'] if 'vk_access_token' in config_json else None
    return public_walls, private_walls, bot_token, user_ids, access_token


def main(argv):
    global storage
    try:
        (opts, args) = getopt.getopt(argv, 'h:')
    except getopt.GetoptError:
        print (help_message)
        sys.exit(1)

    if len(args) == 0:
        print (help_message)
        sys.exit(1)

    for (opt, arg) in opts:
        if opt == '-h':
            print (help_message)
            sys.exit()

    config_file = realpath(args[0])
    
    logfile = config_file.replace('json', 'log')
    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    storagefile = config_file.replace('json', 'db')
    try:
        storage = shelve.open(storagefile)
    except Exception as e:
        print ("Failed to open storage: " + str(e))
        sys.exit(1)

    try:
        last_fetch_time = storage['last_fetch_time']
    except:
        print("last_fetch_time 0")
        last_fetch_time = 1472293178
    #last_fetch_time = 1472293178

    try:
        
        public_walls, private_walls, bot_token, user_ids, access_token = _read_config(config_file)
        while True:
            fetch_time = time.time()
            posts = vk_fetcher.fetch(public_walls, private_walls, last_fetch_time, access_token)
            last_fetch_time = fetch_time
            storage['last_fetch_time'] = fetch_time
            if posts:
                telegram_sender.send(posts, bot_token, user_ids)
            time.sleep(constants.SLEEP_TIME)

    except KeyboardInterrupt:
        pass
    finally:
        print('Closing storage')
        storage.close()

if __name__ == '__main__':
    main(sys.argv[1:])
