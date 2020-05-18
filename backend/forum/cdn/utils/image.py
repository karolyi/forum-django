from PIL.Image import Image


def has_alpha(image: Image) -> bool:
    'Return `True` if the image has an alpha channel (transparency).'
    image.mode
    return \
        image.mode in ('RGBA', 'LA') or \
        (image.mode == 'P' and image.info.get('transparency') is not None)
