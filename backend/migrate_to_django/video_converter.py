import urllib
from urllib.parse import parse_qsl, urlparse

import requests
from bs4 import BeautifulSoup as bs
from bs4.element import Tag
from requests.exceptions import RequestException

import magic
from variables import NONE_SRC

mime = magic.Magic(mime=True)


def is_not_200(video_url):
    try:
        response = requests.head(url=video_url, verify=False, timeout=10)
    except RequestException:
        response = None
    if not response or response.status_code != 200:
        return True
    return False


def get_flash_objects(html):
    object_list = html.select('object')
    return object_list


def filter_video_url(object_item):
    param_obj = object_item.select('param[name=movie]')
    if not len(param_obj):
        return
    url = param_obj[0].get('value')
    if not url or url.lower().endswith('.jpg'):
        return
    return url


def make_empty(object_item):
    none_img = bs(
        markup=f'<img src="{NONE_SRC}" class="notfound-embed">',
        features='lxml').img
    object_item.replace_with(none_img)


def parse_parameters(video_url):
    url_obj = urlparse(video_url)
    if not url_obj:
        return
    return parse_qsl(url_obj.query)


def get_parameter(video_url, parameter_name):
    parameters = parse_parameters(video_url)
    for parameter, value in parameters:
        if parameter == parameter_name:
            return value
    return


def create_flash_string(video_url):
    return (
        '<div class="player-wrapper">\n'
        '<object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" '
        'width="100%%" height="100%%">\n'
        '<param name="movie" value="%s" />\n'
        '<param name="pluginspage" '
        'value="http://www.macromedia.com/go/getflashplayer" />\n'
        '<param name="allowScriptAccess" value="always" />\n'
        '<param name="allowFullScreen" value="true" />\n'
        '<!--[if !IE]>-->\n'
        '<object type="application/x-shockwave-flash" data="%s" '
        'width="100%%" height="100%%"></object>\n'
        '<!--<![endif]-->\n'
        '</object>\n</div>') % (video_url, video_url)


def create_embed_obj(html_string, ratio_class):
    embed_obj = bs(markup=(
        f'<div class="embedded-player {ratio_class}">{html_string}</div>'),
        features='lxml').div
    return embed_obj


def get_soundcloud_player(video_url):
    sound_url = get_parameter(video_url, 'url')
    if is_not_200(sound_url):
        return None, None
    html_string = (
        '<iframe class="player-wrapper" '
        'src="https://w.soundcloud.com/player/?url=%s&show_artwork=true'
        '&auto_play=false"></iframe>') % urllib.quote(sound_url)
    return create_embed_obj(html_string, 'maxheight-166'), sound_url


def get_youtube_player(video_url):
    """
    Bootstrap:
    screen-lg: 1200px
    screen-md: 992px
    screen-sm: 768px
    screen-xs: 480px
    """
    try:
        video_id = urlparse(video_url).path.split('/')[-1].split('&')[0]
    except (ValueError, TypeError, UnicodeError):
        return None, None
    # It seems that youtube starts to redirect after a certain amount
    # of requests
    # if is_not_200(
    #         'http://gdata.youtube.com/feeds/api/videos/%s?v=2&alt=json' % (
    #             video_id)):
    #     return

    # html_string = (
    #     '<iframe class="player-wrapper" '
    #     'src="https://www.youtube.com/embed/%s" frameborder="0">'
    #     '</iframe>') % video_id

    # http://stackoverflow.com/a/2068371
    md_url = 'https://youtu.be/%s' % video_id
    html_string = (
        '<picture class="preview-youtube" data-id="%(video_id)s">'
        '<source media="(min-width: 1200px)" '
        'srcset="%(yt_img)s%(video_id)s/maxresdefault.jpg">'
        # '<source media="(min-width: 992px)" '
        # 'srcset="%(yt_img)s%(video_id)s/hqdefault.jpg">'
        '<source media="(min-width: 768px)" '
        'srcset="%(yt_img)s%(video_id)s/hqdefault.jpg">'
        '<source media="(min-width: 480px)" '
        'srcset="%(yt_img)s%(video_id)s/sddefault.jpg">'
        '<source srcset="%(yt_img)s%(video_id)s/default.jpg">'
        '<img src="%(yt_img)s%(video_id)s/default.jpg">'
        '</picture>') % {
        'yt_img': 'https://img.youtube.com/vi/',
        'video_id': video_id
    }
    return create_embed_obj(html_string, 'ratio-16-9'), md_url


def get_audio_player(video_url):
    path = get_parameter(video_url, 'path')
    if not path.startswith('http') or is_not_200(path):
        return None, None
    html_string = (
        '<div class="player-wrapper">'
        '<audio width="100%%" height="100%%" controls>'
        '<source src="%s"/></audio></div>') % path
    md_url = path
    return create_embed_obj(html_string, 'maxheight-40'), md_url


def get_vimeo_player(video_url):
    clip_id = get_parameter(video_url, 'clip_id')
    md_url = 'https://vimeo.com/%s' % clip_id
    if is_not_200(md_url):
        return None, None
    html_string = (
        '<iframe class="player-wrapper" '
        'src="https://player.vimeo.com/video/%s" frameborder="0">'
        '</iframe>') % clip_id
    return create_embed_obj(html_string, 'ratio-16-9'), md_url


def get_flash_player(video_url):
    if is_not_200(video_url):
        return None, None
    return create_embed_obj(
        create_flash_string(video_url), 'ratio-16-9'), video_url


def get_indavideo_player(video_url):
    video_id = get_parameter(video_url, 'vID')
    try:
        content = requests.get(
            'http://embed.indavideo.hu/player/video/%s/' % video_id)\
            .content.encode('utf-8')
    except RequestException:
        return None, None
    if "['_trackEvent', 'Player', 'Nincs ilyen video']" in content:
        return None, None
    html_string = (
        '<iframe class="player-wrapper" '
        'src="http://embed.indavideo.hu/player/video/%s/">'
        '</iframe>') % video_id
    md_url = 'http://indavideo.hu/video/%s' % video_id
    return create_embed_obj(html_string, 'ratio-16-9'), md_url


def get_dailymotion_player(video_url):
    try:
        path_last_element = urlparse(video_url).path.split('/')[-1]
    except (ValueError, TypeError, UnicodeError):
        return None, None
    md_url = 'http://www.dailymotion.com/video/%s' % path_last_element
    if is_not_200(md_url):
        return None, None
    html_string = (
        '<iframe frameborder="0" class="player-wrapper" '
        'src="http://www.dailymotion.com/embed/video/%s"></iframe>'
    ) % path_last_element
    return create_embed_obj(html_string, 'ratio-16-9'), md_url


def get_videa_player(video_url):
    video_id = get_parameter(video_url, 'v')
    html_string = (
        '<iframe class="player-wrapper" '
        'src="http://videa.hu/player?v=%s" frameborder="0"></iframe>'
    ) % video_id
    md_url = 'http://videa.hu/videok/%s' % video_id
    return create_embed_obj(html_string, 'ratio-16-9'), md_url


def get_liveleak_player(video_url):
    try:
        path_last_element = urlparse(video_url).path.split('/')[-1]
        page_html = bs(
            markup=requests.get(
                'http://www.liveleak.com/view?i=%s' % path_last_element
            ).content, features='lxml')
        embed_code_a = page_html.select(
            'div#leftcol span a.form_button')[0].get('onclick')
        video_id = embed_code_a.split('\'')[1]
    except (ValueError, TypeError, UnicodeError, RequestException):
        return None, None
    html_string = (
        '<iframe class="player-wrapper" '
        'src="http://www.liveleak.com/ll_embed?f=%s"></iframe>') % video_id
    md_url = 'http://www.liveleak.com/view?i=%s' % path_last_element
    return create_embed_obj(html_string, 'ratio-16-9'), md_url


def get_bad_youtube_player(video_url):
    video_id = get_parameter(video_url, 'v')
    return get_youtube_player('youtube.com/v/%s' % video_id)


def get_facebook_video_embed(video_url):
    video_id = get_parameter(video_url, 'video_id')
    html_string = (
        '<iframe src="https://www.facebook.com/video/embed?video_id=%s" '
        'class="player-wrapper" frameborder="0"></iframe>') % video_id
    md_url = 'https://www.facebook.com/video.php?v=%s' % video_id
    return create_embed_obj(html_string, 'ratio-16-9'), md_url


def get_facebook_player(video_url):
    try:
        path_last_element = urlparse(video_url).path.split('/')[-1]
    except (ValueError, TypeError, UnicodeError):
        return None, None
    html_string = (
        '<iframe src="https://www.facebook.com/video/embed?video_id=%s" '
        'class="player-wrapper" frameborder="0"></iframe>') % path_last_element
    md_url = 'https://www.facebook.com/video.php?v=%s' % path_last_element
    return create_embed_obj(html_string, 'ratio-16-9'), md_url


def get_metacafe_player(video_url):
    try:
        path_element = urlparse(video_url).path.split('/')[2]
    except (ValueError, TypeError, UnicodeError):
        return None, None
    html_string = (
        '<iframe src="http://www.metacafe.com/embed/%s/" '
        'class="player-wrapper" frameborder="0"></iframe>') % path_element
    md_url = 'http://www.metacafe.com/w/%s' % path_element
    return create_embed_obj(html_string, 'ratio-16-9'), md_url


def get_movieweb_player(video_url):
    try:
        path_last_element = urlparse(video_url).path.split('/')[-1]
    except (ValueError, TypeError, UnicodeError):
        return None, None
    html_string = (
        '<iframe src="http://www.movieweb.com/v/%s/embed_video" '
        'class="player-wrapper" frameborder="0"></iframe>') % path_last_element
    md_url = 'http://www.movieweb.com/v/%s/embed_video' % path_last_element
    return create_embed_obj(html_string, 'ratio-16-9'), md_url


def get_mixcloud_player(video_url):
    try:
        feed_url = get_parameter(video_url, 'feed')
        json_response = requests.get(
            url='http://www.mixcloud.com/oembed/?url=%s&format=json' %
            urllib.quote(feed_url), verify=False, timeout=10).json()
        html = bs(json_response['html'])
        url = html.select('iframe')[0].get('src')
    except RequestException:
        return None, None
    html_string = (
        '<iframe src="%s" class="player-wrapper" frameborder="0">'
        '</iframe>') % url
    return create_embed_obj(html_string, 'ratio-1-1'), feed_url


def create_player_if_flash(video_url):
    try:
        req_obj = requests.get(url=video_url, verify=False, timeout=10)
        mime_type = mime.from_buffer(buf=req_obj.content)
    except RequestException:
        return None, None
    if mime_type != 'application/x-shockwave-flash; charset=binary':
        return None, None
    return get_flash_player(video_url)


def find_embed_string(video_url):
    if 'player.soundcloud.com/player.swf' in video_url:
        return get_soundcloud_player(video_url)
    if 'youtube.com/v/' in video_url\
            or 'youtube-nocookie.com/v/' in video_url\
            or 'youtube.com/e/' in video_url\
            or 'www.youtube.com/watch/v/' in video_url\
            or 'www.youtube.com/embed/' in video_url\
            or 'youtu.be/' in video_url:
        return get_youtube_player(video_url)
    if 'sound.swf?path=' in video_url:
        return get_audio_player(video_url)
    if '//vimeo.com/moogaloop.swf?clip_id=' in video_url:
        return get_vimeo_player(video_url)
    if '//files.indavideo.hu/player/gup.swf?' in video_url\
            or '//files.indavideo.hu/player/vc_o.swf?vID' in video_url\
            or '//assets.indavideo.hu/swf/player.swf?vID=' in video_url:
        return get_indavideo_player(video_url)
    if 'streetfire.net/vidiac.swf?video=' in video_url:
        # streetfire.net doesn't exist anymore
        return None, None
    if 'www.dailymotion.com/swf/' in video_url:
        return get_dailymotion_player(video_url)
    if 'blip.tv/play/' in video_url:
        # streetfire.net doesn't exist anymore
        return None, None
    if 'videa.hu/flvplayer.swf?v=' in video_url:
        return get_videa_player(video_url)
    if 'www.liveleak.com/e/' in video_url:
        return get_liveleak_player(video_url)
    if '//www.youtube.com/watch?' in video_url:
        return get_bad_youtube_player(video_url)
    if 'tv.gamestar.hu/player/' in video_url\
            or 'www.traileraddict.com/emd/' in video_url\
            or '.zippyshare.com/swf/player_local.swf' in video_url\
            or 'www.hks-tv.com/watch_vx/hks_vxs.swf?watch=' in video_url:
        return get_flash_player(video_url)
    if 'facebook.com/v/' in video_url:
        return get_facebook_player(video_url)
    if 'facebook.com/video/embed?' in video_url:
        return get_facebook_video_embed(video_url)
    if 'www.metacafe.com/fplayer/' in video_url:
        return get_metacafe_player(video_url)
    if 'movieweb.com/v/' in video_url:
        return get_movieweb_player(video_url)
    if 'www.mixcloud.com/media/swf/player/mixcloudLoader.swf?' in video_url:
        return get_mixcloud_player(video_url)
    if 'www.freevlog.h' in video_url\
            or 'www.gametrailers.com/remote_wrap.php' in video_url:
        # freevlog.hu doesn't exist anymore
        # gametrailers.com does not provide a good url
        return None, None
    return create_player_if_flash(video_url)


def replace_video(object_item, video_url):
    embed_obj, md_url = find_embed_string(video_url)
    if not embed_obj:
        make_empty(object_item)
        return
    embed_obj.md_url = md_url
    object_item.replace_with(embed_obj)


def parse_videos(html: Tag):
    # TODO: esemenyek/adatlapok markdownba, videokkal
    object_list = get_flash_objects(html)
    for object_item in object_list:
        video_url = filter_video_url(object_item)
        if not video_url:
            make_empty(object_item)
            continue
        replace_video(object_item, video_url)


# def html_to_md(content):
#     """
#     Convert parsed videos content to markdown.
#     """
#     for item in content.find('.notfound-embed'):
#         item.replace_with(item.markdown_content)
