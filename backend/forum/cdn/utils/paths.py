from os import chown
from pathlib import Path
from re import compile as re_compile

from django.conf import settings
from PIL.Image import Image
from unidecode import unidecode

from forum.utils import slugify
from forum.utils.locking import MAX_FILENAME_SIZE, TempLock

FILE_SIMPLER_RE = re_compile(r'[^a-zA-Z0-9.\-]+')
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
UNNECESSARY_FILENAME_PARTS = (
    'www.kepfeltoltes.hu',
    'www_kepfeltoltes_hu',
    'www-kepfeltoltes-hu',
    'wwwkepfeltolteshu',
    'wwwkepfeltoltes',
)


def get_path_with_ensured_dirs(path_elements: list) -> Path:
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
    while _iter_metapath:
        lock_name = ('ensure-dir-' + slugify(
            input_data='-'.join(lock_namelist)))[:MAX_FILENAME_SIZE]
        with TempLock(name=lock_name):
            if not new_absolute_path.is_dir():
                new_absolute_path.mkdir(mode=mode_dir)
                chown(path=new_absolute_path, uid=-1, gid=gid)
        _iter_pathitem = _iter_metapath.pop(0)
        new_absolute_path = new_absolute_path.joinpath(_iter_pathitem)
        lock_namelist.append(_iter_pathitem)
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


def normalize_filename(filename: Path, mime_type: str) -> str:
    filename = Path(unidecode(
        string=remove_unnecessary_filename_parts(filename=filename)))
    name = FILE_SIMPLER_RE.sub('-', filename.stem).strip('-')
    extension = get_extension(mime_type)
    if len(str(filename)) > MAX_FILENAME_SIZE:
        name = name[:MAX_FILENAME_SIZE - len(extension)]
    return '.'.join((name, extension))


def remove_unnecessary_filename_parts(filename: Path) -> str:
    changed = original = str(filename)
    for unnecessary_part in UNNECESSARY_FILENAME_PARTS:
        changed = changed.replace(unnecessary_part, '')
    return original if original == changed else changed
