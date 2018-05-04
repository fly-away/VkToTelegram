"""Fetch new posts from vk communities walls"""

import collections
import logging
import requests
import constants
import sys
import time

logger = logging.getLogger('vk_fetcher')


def fetch(public_walls, private_walls, last_fetch_time, access_token):
    logger.debug('fetch(%s, %s)', public_walls, last_fetch_time)

    posts = []

    if public_walls is not None:
        for wall in public_walls:
            posts.extend(_get_wall_posts(wall, last_fetch_time, None))
            time.sleep(5)

    if private_walls is not None:
        for wall in private_walls:
            posts.extend(_get_wall_posts(wall, last_fetch_time, access_token))
            time.sleep(5)

    return posts

def _get_wall_posts(wall, last_fetch_time, access_token):
    logger.debug('_get_wall_posts(%s, %s)', wall, last_fetch_time)

    new_posts = []
    url = constants.VK_PUBLIC_WALL_URL.format(wall) if access_token is None \
        else constants.VK_PRIVATE_WALL_URL.format(wall, access_token)

    requests_ok = False
    for num in range(1,5):
        try:
            response = requests.get(url)
            logger.debug('get ' + url)
        except Exception as e:
            logger.error ("mg Unexpected error: " + str(e))
            time.sleep(num)    
        else:
            requests_ok = True
            break

    if requests_ok and response.status_code == requests.codes.ok:
        try:
            json_data = response.json()
            items = json_data['response']['items']
            for i in items:
                if i['date'] > last_fetch_time:
                    nopreview = 1
                    try:
                        text = i['text']
                        link = next( filter(lambda x: x['type'] == 'link', i['attachments']) )
                        link = link['link']
                        if not text:
                            nopreview = 0
                        if ( text.find(link['url']) == -1 ):
                            text = text + "\n" + link['url']
                            print('link attached to text: ' + link)
                    except KeyError as e:
                        logger.info ('KeyError "%s"' % str(e))
                    except Exception as e:
                        logger.error ("ik Unexpected error: " + str(e))
                    new_posts.append({'wall': wall, 'text': text, 'nopreview': nopreview})
        except KeyError as e:
            logger.error ('KeyError "%s"' % str(e))
            logger.error (response.text)
        except Exception as e:
            logger.error ("Unexpected error: " + str(e))
            logger.error (response.text)
            
    logger.debug('new posts count : %s', len(new_posts))

    #print(new_posts)
    return new_posts


def _format_post_url(wall, post):
    return constants.VK_POST_URL.format(wall, post['to_id'], post['id'])


def _get_photos(post):
    if 'attachments' in post:
        return map(lambda x: x['photo']['src_big'], filter(lambda x: x['type'] == 'photo', post['attachments']))
