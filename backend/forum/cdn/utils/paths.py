from os import chown, umask
from pathlib import Path
from typing import Iterable

from django.conf import settings
from PIL.Image import Image

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
FILE_EXTENSIONS_KEYSET = set(FILE_EXTENSIONS)


def get_path_with_ensured_dirs(path_elements: Iterable) -> Path:
    """
    Return a CDN `Path` while ensuring the directories up until the file
    (last part) with the right attributes.
    """
    requested_size, *_iter_metapath = path_elements
    new_absolute_path = Path(
        settings.CDN['PATH_SIZES'][requested_size]).absolute()
    mode_dir = settings.CDN['POSIXFLAGS']['mode_dir']
    gid = settings.CDN['POSIXFLAGS']['gid']
    lock_namelist = [requested_size]
    old_umask = umask(0o777 - mode_dir)
    while _iter_metapath:
        new_absolute_path.mkdir(exist_ok=True)
        chown(path=new_absolute_path, uid=-1, gid=gid)
        _iter_pathitem = _iter_metapath.pop(0)
        new_absolute_path = new_absolute_path.joinpath(_iter_pathitem)
        lock_namelist.append(_iter_pathitem)
    umask(old_umask)
    return new_absolute_path


def set_cdn_fileattrs(path: Path):
    'Set CDN file attributes.'
    chown(path=path, uid=-1, gid=settings.CDN['POSIXFLAGS']['gid'])
    if path.is_file():
        path.chmod(mode=settings.CDN['POSIXFLAGS']['mode_file'])
    elif path.is_symlink():
        path.chmod(mode=settings.CDN['POSIXFLAGS']['mode_link'])


def save_new_image(image: Image, new_path: Path, save_kwargs: dict):
    'Save the image and ensure its mode/gid.'
    temp_path = Path(new_path).parent.joinpath(f'temp-{new_path.name}')
    image.save(fp=temp_path, **save_kwargs)
    set_cdn_fileattrs(path=temp_path)
    temp_path.rename(new_path)


def get_extension(mime_type) -> str:
    for mime_type_config in FILE_EXTENSIONS:
        if mime_type.startswith(mime_type_config):
            return FILE_EXTENSIONS[mime_type_config]
    return 'jpg'
