from contextlib import contextmanager
from datetime import datetime
from io import TextIOWrapper
from logging import (
    DEBUG, Formatter, Logger, RootLogger, StreamHandler, getLogger)
from tempfile import TemporaryFile
from time import time

from django.conf import settings

from forum.utils.locking import PATH_TEMPLOCK_DIR
from forum.utils.pathlib import Path

ONE_WEEK_AGO = time() - 60 * 60 * 24 * 7
PATH_SIZES_SET = set(settings.CDN['PATH_SIZES'].values())
_LOGGER = getLogger(name=__name__)
_ROOTLOGGER = Logger.root  # type: RootLogger


def _clear_templocks():
    'Delete old templock files.'
    one_hour_ago = time() - 60 * 60
    for path in PATH_TEMPLOCK_DIR.glob(pattern='*'):
        if path.stat().st_mtime <= one_hour_ago:
            path.unlink()


def _clean_watermarked_originals():
    """
    Clean up `original` watermarked files if they are old AND none of
    the symlinks within the CDN pointing to them are old.
    """
    root_original = settings.CDN['PATH_SIZES']['original']  # type: Path
    relative_list = list(
        path.relative_to(root_original)
        for path in root_original.rglob(pattern='*')
        if path.is_file() and path.stat().st_mtime <= ONE_WEEK_AGO)
    for relative in relative_list:
        to_delete = True
        for size in settings.CDN['MAXWIDTH']:
            root_size = settings.CDN['PATH_SIZES'][size]  # type: Path
            size_path = root_size.joinpath(relative)
            if not size_path.is_symlink():
                continue
            mtime = size_path.lstat().st_mtime
            if mtime > ONE_WEEK_AGO:
                to_delete = False
                continue
            path_date = datetime.fromtimestamp(mtime).strftime('%c')
            _LOGGER.info(msg=f'Removing {size_path!r}: {path_date}')
            size_path.remove_up_to(parent=root_size)
        if to_delete:
            abs_path = root_original.joinpath(relative)
            path_date = \
                datetime.fromtimestamp(abs_path.stat().st_mtime).strftime('%c')
            _LOGGER.info(msg=f'Removing {abs_path!r}: {path_date}')
            abs_path.remove_up_to(parent=root_original)


def _clean_old_sizes():
    'Go through the sized images and delete them if they are old.'
    for size in settings.CDN['MAXWIDTH']:
        root_size = settings.CDN['PATH_SIZES'][size]  # type: Path
        path_list = list(
            path for path in root_size.rglob(pattern='*')
            if path.is_symlink() or path.is_file())
        for path in path_list:  # type: Path
            mtime = path.lstat().st_mtime if path.is_symlink() \
                else path.stat().st_mtime
            if mtime > ONE_WEEK_AGO and path.exists():
                # is newer AND resolves as a symlink
                continue
            path_date = datetime.fromtimestamp(mtime).strftime('%c')
            _LOGGER.info(msg=f'Removing {path!r}: {path_date}')
            path.remove_up_to(parent=root_size)


@contextmanager
def _setup_logging() -> TextIOWrapper:
    with TemporaryFile(mode='r+') as fd:
        stream_handler = StreamHandler(stream=fd)
        stream_handler.setFormatter(fmt=Formatter(
            fmt='%(levelname)s:%(asctime)s:%(name)s:%(message)s'))
        _ROOTLOGGER.addHandler(hdlr=stream_handler)
        _ROOTLOGGER.setLevel(level=DEBUG)
        try:
            yield fd
        finally:
            _ROOTLOGGER.removeHandler(hdlr=stream_handler)
            fd.seek(0)
            lines = fd.readlines()
            if len(lines) > 2:
                print(''.join(lines))


def run():
    'Run maintenance.'
    with _setup_logging():
        _clear_templocks()
        _LOGGER.info(msg='====== Clear watermarked originals:')
        _clean_watermarked_originals()
        _LOGGER.info(msg='====== Clear old sizes:')
        _clean_old_sizes()
