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

SUCCESSFULLY_DOWNLOADED = 0
CDN_NO_MODEL = 0
CDN_NO_FILE = 0
DEAD_HOSTERS = ('http://imagerz.com/',)
