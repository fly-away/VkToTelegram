"""Various constants."""

from __future__ import unicode_literals

VK_PUBLIC_WALL_URL = 'https://api.vk.com/method/wall.get?domain={0}&count=5&v=5.53'

VK_PRIVATE_WALL_URL = 'https://api.vk.com/method/wall.get?domain={0}&count=5&access_token={2}&v=5.53'

VK_POST_URL = 'https://vk.com/{0}?w=wall{1}_{2}'

TELEGRAM_URL = 'https://api.telegram.org/bot{0}/sendMessage'

TELEGRAM_MESSAGE_TEMPLATE = u'{0}'

DEBUG_SLEEP_TIME = 5
'''10 seconds between fetches for debug'''

SLEEP_TIME = 60
'''5 minutes between fetches'''
