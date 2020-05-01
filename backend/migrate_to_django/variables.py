from pathlib import Path

import MySQLdb
from django.conf import settings

conn = MySQLdb.connect(**settings.CRXFORUM_CONNECTION)

user_dict = {}
topic_dict = {}
session_dict = {}
message_dict = {}
comment_uniqid_dict = {}
event_dict = {}

NONE_SRC = '/static/images/image-404.svg'
CDN_FILES_ROOT = Path('~', 'cdn', 'original').expanduser()
HTTP_CDN_SIZE_ORIGINAL = '/'.join((settings.CDN['URL_PREFIX'], 'original'))
HTTP_CDN_SIZEURLS = {
    x: '/'.join([settings.CDN['URL_PREFIX'], x])
    for x in settings.CDN['IMAGESIZE']
}

INNER_IMAGE_URLS = (
    '/static/skins/', '/static/images/', NONE_SRC, HTTP_CDN_SIZE_ORIGINAL,
    *HTTP_CDN_SIZEURLS.values())
OLD_SELF_URL = 'http://crxforum.flix.hu'
MISSING_IMAGE_COUNT = 0
ALREADY_MISSING_IMAGE_COUNT = 0
ALREADY_DOWNLOADED_IMAGE_COUNT = 0
FILE_EXTENSIONS = {
    'image/jpeg': 'jpg',
    'image/gif': 'gif',
    'image/tiff': 'tif',
    'image/png': 'png',
    'image/x-ms-bmp': 'bmp',
    'image/x-icon': 'ico',
    'image/webp': 'webp',
    'image/svg+xml': 'svg',
}
FILE_EXTENSIONS_KEYSET = set(FILE_EXTENSIONS.keys())

CANCEL_HASH_TUPLE = (
    'cc2aa0e463e98c8f9a35ca3bfc244eb5c1426df254905286e34ac55956d8d02f'
    '63e0183406b6003f36096909bfcb82b8af68c6454ecf2f42cdbfaef92c9587bd',
)
UNNECESSARY_FILENAME_PARTS = (
    'www.kepfeltoltes.hu',
    'www_kepfeltoltes_hu',
    'www-kepfeltoltes-hu',
    'wwwkepfeltolteshu',
    'wwwkepfeltoltes',
)
FILENAME_MAXLENGTH = 80
SUCCESSFULLY_DOWNLOADED = 0
CDN_NO_MODEL = 0
CDN_NO_FILE = 0
DEAD_HOSTERS = ('http://imagerz.com/',)
