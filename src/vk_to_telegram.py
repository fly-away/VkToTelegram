#!/usr/bin/env python3.5
"""The main module"""

import json
import getopt
import sys
import time
from os.path import realpath
import constants
import telegram_sender
import vk_fetcher
import logging

help_message = 'vk_to_telegram.py config.json'


def _read_config(config_file):
    config_json = json.loads(open(config_file).read())

    public_walls = config_json['public_walls'] if 'public_walls' in config_json else None
    bot_token = config_json['telegram_bot_token']
    user_ids = config_json['user_ids']
    access_token = config_json['vk_access_token'] if 'vk_access_token' in config_json else None
    return public_walls, bot_token, user_ids, access_token


def main(argv):
    backlog_time = 86000
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
    logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', datefmt='%m/%d/%Y %H:%M:%S %Z', filename=logfile, level=logging.WARNING)
    logger = logging.getLogger('vk_to_telegram')
    storagefile = config_file.replace('json', 'last_check')

    try:
        with open(storagefile) as f:
            last_fetch_time = int(f.readline().strip())
    except Exception as e:
        logger.error ("Failed to open storage: " + str(e))
        last_fetch_time = int(time.time()) - backlog_time

    min_last_fetch_time = int(time.time()) - backlog_time
    if ( last_fetch_time < min_last_fetch_time ):
        last_fetch_time = min_last_fetch_time

    last_fetch_time_human_readable = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(last_fetch_time))
    logmsg="starting from {}, epoch time {}".format( last_fetch_time_human_readable, last_fetch_time)
    print(logmsg)
    logger.warning(logmsg)

    try:
        
        public_walls, bot_token, user_ids, access_token = _read_config(config_file)
        while True:
            fetch_time = int(time.time())
            posts = vk_fetcher.fetch(public_walls, last_fetch_time, access_token)
            last_fetch_time = fetch_time
            with open(storagefile, "w") as text_file:
                    text_file.write(str(fetch_time) + "\n")
                    text_file.write(time.strftime("%Y-%m-%d %H:%M:%S %Z\n", time.localtime(fetch_time)))
            if posts:
                #print (posts)
                telegram_sender.send(posts, bot_token, user_ids)
            time.sleep(constants.SLEEP_TIME)

    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main(sys.argv[1:])
