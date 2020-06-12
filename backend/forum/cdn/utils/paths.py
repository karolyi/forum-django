from os import chown

from django.conf import settings
from PIL.Image import Image

from forum.utils.pathlib import Path

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
