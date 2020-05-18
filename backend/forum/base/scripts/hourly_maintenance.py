from datetime import datetime
from pathlib import Path
from time import time

from django.conf import settings

from forum.utils.locking import PATH_TEMPLOCK_DIR


def _clear_templocks():
    'Delete old templock files.'
    one_hour_ago = time() - 60 * 60
    for path in PATH_TEMPLOCK_DIR.glob(pattern='*'):
        if path.stat().st_mtime <= one_hour_ago:
            path.unlink()


def _clear_old_converted_cdnfiles():
    'Delete old CDN files that were a result of a conversion.'
    one_week_ago = time() - 60 * 60 * 24 * 7
    for size in settings.CDN['MAXWIDTH']:
        for path in settings.CDN['PATH_SIZES'][size].rglob(
                pattern='*'):  # type: Path
            if path.is_symlink():
                if path.lstat().st_mtime <= one_week_ago:
                    file_date = datetime.fromtimestamp(
                        path.lstat().st_mtime).strftime('%c')
                    path.unlink()
                    print(f'Removed symlink: {path} ({file_date})')
            elif path.is_file():
                if path.stat().st_mtime <= one_week_ago:
                    file_date = datetime.fromtimestamp(
                        path.stat().st_mtime).strftime('%c')
                    path.unlink()
                    print(f'Removed file: {path} ({file_date})')
            elif path.is_dir():
                if path.stat().st_mtime <= one_week_ago:
                    try:
                        file_date = datetime.fromtimestamp(
                            path.stat().st_mtime).strftime('%c')
                        path.rmdir()
                        print(f'Removed directory {path}')
                    except OSError as exc:
                        if exc.args[0] != 66:
                            raise


def run():
    'Run maintenance.'
    _clear_templocks()
    _clear_old_converted_cdnfiles()
