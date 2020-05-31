from datetime import datetime
from pathlib import Path
from time import time

from django.conf import settings

from forum.utils.locking import PATH_TEMPLOCK_DIR

one_week_ago = time() - 60 * 60 * 24 * 7
PATH_SIZES_SET = set(settings.CDN['PATH_SIZES'].values())


def _clear_templocks():
    'Delete old templock files.'
    one_hour_ago = time() - 60 * 60
    for path in PATH_TEMPLOCK_DIR.glob(pattern='*'):
        if path.stat().st_mtime <= one_hour_ago:
            path.unlink()


def _destroy_path(path: Path):
    'Delete a directory or file. It must exist.'
    filetype = 'symlink' if path.is_symlink() else \
        'file' if path.is_file() else \
        'directory' if path.is_dir() else 'unknown type'
    stat = path.lstat() if filetype == 'symlink' else path.stat()
    path_date = datetime.fromtimestamp(stat.st_mtime).strftime('%c')
    if filetype != 'directory':
        path.unlink()
    else:
        try:
            path.rmdir()
        except OSError as exc:
            if exc.args[0] != 66:
                raise
    print(f'Removed {filetype} {path!r} ({path_date})')


def _unlink_parents(path: Path):
    'Unlink parents of the path.'
    while True:
        path = path.parent.resolve()
        if path in PATH_SIZES_SET:
            return
        if not path.exists():
            continue
        _destroy_path(path=path)


def _unlink_path_and_parents(path: Path):
    'Unlink a file and its containing directories without errors.'
    path = path.resolve()
    if not path.exists():
        return
    try:
        path.relative_to(settings.CDN['PATH_ROOT'])
    except ValueError:
        return
    _destroy_path(path=path)
    _unlink_parents(path=path)


def _clear_old_converted_sized_cdnfiles():
    'Delete old CDN files that were a result of a conversion.'
    for size in settings.CDN['MAXWIDTH']:
        size_path = settings.CDN['PATH_SIZES'][size]  # type: Path
        for path in size_path.rglob(pattern='*'):  # type: Path
            if path.is_symlink():
                if path.lstat().st_mtime <= one_week_ago:
                    _unlink_path_and_parents(path=path)
            elif path.is_file() or path.is_dir():
                if path.stat().st_mtime <= one_week_ago:
                    _unlink_path_and_parents(path=path)


def _clean_watermarked_originals():
    'Clean up `original` watermarked files.'
    original_path = settings.CDN['PATH_SIZES']['original']  # type: Path
    relative_list = list(
        path.relative_to(original_path)
        for path in original_path.rglob(pattern='*')
        if path.is_file() and path.stat().st_mtime <= one_week_ago)
    for relative in relative_list:
        for size in settings.CDN['MAXWIDTH']:
            size_path = settings.CDN['PATH_SIZES'][size]  # type: Path
            size_path = size_path.joinpath(relative)
            _unlink_path_and_parents(path=size_path)
        _unlink_path_and_parents(path=original_path.joinpath(relative))


def run():
    'Run maintenance.'
    _clear_templocks()
    _clean_watermarked_originals()
    _clear_old_converted_sized_cdnfiles()
