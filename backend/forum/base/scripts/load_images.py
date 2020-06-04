from django.conf import settings
from PIL import Image as PilImage
from PIL import UnidentifiedImageError

from forum.cdn.models import Image


def run():
    all_images = list()
    to_delete = set()
    for idx, image in enumerate(Image.objects.all()):  # type: int, Image
        if idx % 1000 == 0:
            print(idx)
        abs_path = \
            settings.CDN['PATH_SIZES']['downloaded'].joinpath(image.cdn_path)
        try:
            with PilImage.open(fp=abs_path) as pil_image:
                image.width, image.height = pil_image.size
                all_images.append(image)
        except UnidentifiedImageError:
            to_delete.add(image.pk)
    Image.objects.bulk_update(
        objs=all_images, fields=['width', 'height'], batch_size=500)
    print('to delete:', to_delete)
    Image.objects.filter(pk__in=to_delete).delete()
