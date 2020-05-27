import MySQLdb
from django.conf import settings

conn = MySQLdb.connect(**settings.CRXFORUM_CONNECTION)

user_dict = {}
topic_dict = {}
session_dict = {}
message_dict = {}
comment_uniqid_dict = {}
event_dict = {}

INNER_IMAGE_URLS = (
    '/static/skins/', '/static/images/', settings.IMG_404_PATH,
    *settings.CDN['URLPREFIX_SIZE'].values())
OLD_SELF_URL = 'http://crxforum.flix.hu'
MISSING_IMAGE_COUNT = 0
ALREADY_MISSING_IMAGE_COUNT = 0
ALREADY_DOWNLOADED_IMAGE_COUNT = 0

CANCEL_HASH_TUPLE = (
    'cc2aa0e463e98c8f9a35ca3bfc244eb5c1426df254905286e34ac55956d8d02f'
    '63e0183406b6003f36096909bfcb82b8af68c6454ecf2f42cdbfaef92c9587bd',
)
SUCCESSFULLY_DOWNLOADED = 0
CDN_NO_MODEL = 0
CDN_NO_FILE = 0
DEAD_HOSTERS = ('http://imagerz.com/',)
