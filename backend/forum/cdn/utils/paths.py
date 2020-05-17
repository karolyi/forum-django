from os import chown
from pathlib import Path

from django.conf import settings
from PIL.Image import Image


def get_ensured_dirs_path(path_elements: list) -> Path:
    """
    Ensure the directories up until the file with the right
    mode/gid.
    """
    requested_size, *_iter_metapath = path_elements
    new_absolute_path = Path(
        settings.CDN['PATH_SIZES'][requested_size]).absolute()
    mode_dir = settings.CDN['POSIXFLAGS']['mode_dir']
    gid = settings.CDN['POSIXFLAGS']['gid']
    while _iter_metapath:
        if not new_absolute_path.is_dir():
            new_absolute_path.mkdir(mode=mode_dir)
            chown(path=new_absolute_path, uid=-1, gid=gid)
        new_absolute_path = \
            new_absolute_path.joinpath(_iter_metapath.pop(0))
    return new_absolute_path


def set_file_mode(path: Path):
    'Set CDN file modes and gids.'
    chown(path=path, uid=-1, gid=settings['CDN']['POSIXFLAGS']['gid'])
    path.chmod(mode=settings['CDN']['POSIXFLAGS']['mode_file'])


def save_new_image(image: Image, new_path: Path, save_kwargs: dict):
    'Save the image and ensure its mode/gid.'
    temp_path = Path(new_path).parent.joinpath(f'temp-{new_path.name}')
    image.save(fp=temp_path, **save_kwargs)
    set_file_mode(path=temp_path)
    temp_path.rename(new_path)
