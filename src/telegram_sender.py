"""Send new posts via telegram bot"""

import logging
import constants
import requests
import json

logger = logging.getLogger('telegram_sender')


def send(posts, bot_token, user_ids):
    for post in posts:
        for user_id in user_ids:
            url = constants.TELEGRAM_URL.format(bot_token)
            data={'chat_id': user_id, 'text': constants.TELEGRAM_MESSAGE_TEMPLATE.format(post['text']), 'disable_web_page_preview': post['nopreview']}
            response = requests.post(url, data=data)
            if response.status_code != 200:
                logger.debug('Send telegram status code : %s, text: "%s"', response.status_code, json.loads(response.text))


def _get_photos(photo_urls):
    if photo_urls:
        return reduce(lambda x, y: x + '\n\n' + y, photo_urls)
