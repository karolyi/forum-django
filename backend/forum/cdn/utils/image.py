from collections import defaultdict
from itertools import chain
from random import randrange
from typing import Optional, Tuple

from django.conf import settings
from PIL.Image import Image
from PIL.Image import open as image_open
from PIL.ImageSequence import Iterator as SeqIterator

with image_open(fp=settings.WATERMARK_PATH) as image:
    WATERMARK_IMAGE = image  # type: Image
    WATERMARK_IMAGE = WATERMARK_IMAGE.convert(mode='RGBA')
CONVERSION_MAP = dict(JPEG='RGB')


def has_alpha(image: Image) -> bool:
    'Return `True` if the image has an alpha channel (transparency).'
    image.mode
    return \
        image.mode in ('RGBA', 'LA') or \
        (image.mode == 'P' and image.info.get('transparency') is not None)


class TransparentAnimatedGifConverter(object):
    _PALETTE_SLOTSET = set(range(256))

    def __init__(self, img_rgba: Image, alpha_threshold: int = 0):
        self._img_rgba = img_rgba
        self._alpha_threshold = alpha_threshold

    def _process_pixels(self):
        'Set the transparent pixels to the color 0.'
        self._transparent_pixels = set(
            idx for idx, alpha in enumerate(
                self._img_rgba.getchannel(channel='A').getdata())
            if alpha <= self._alpha_threshold)

    def _set_parsed_palette(self) -> list:
        'Parse the RGB palette color `tuple`s from the palette.'
        palette = self._img_p.getpalette()
        self._img_p_used_palette_idxs = set(
            idx for pal_idx, idx in enumerate(self._img_p_data)
            if pal_idx not in self._transparent_pixels)
        self._img_p_parsedpalette = dict(
            (idx, tuple(palette[idx * 3:idx * 3 + 3]))
            for idx in self._img_p_used_palette_idxs)

    def _get_similar_color_idx(self):
        'Return a palette index with the closest similar color.'
        old_color = self._img_p_parsedpalette[0]
        dict_distance = defaultdict(list)
        for idx in range(1, 256):
            color_item = self._img_p_parsedpalette[idx]
            if color_item == old_color:
                return idx
            distance = sum((
                abs(old_color[0] - color_item[0]),  # Red
                abs(old_color[1] - color_item[1]),  # Green
                abs(old_color[2] - color_item[2])))  # Blue
            dict_distance[distance].append(idx)
        return dict_distance[sorted(dict_distance)[0]][0]

    def _remap_palette_idx_zero(self):
        'Since the first color is used in the palette, remap it.'
        free_slots = self._PALETTE_SLOTSET - self._img_p_used_palette_idxs
        new_idx = free_slots.pop() if free_slots else \
            self._get_similar_color_idx()
        self._img_p_used_palette_idxs.add(new_idx)
        self._palette_replaces['idx_from'].append(0)
        self._palette_replaces['idx_to'].append(new_idx)
        self._img_p_parsedpalette[new_idx] = self._img_p_parsedpalette[0]
        del(self._img_p_parsedpalette[0])

    def _get_unused_color(self) -> tuple:
        """
        Return a color for the palette that does not collide with any
        other already in the palette.
        """
        used_colors = set(self._img_p_parsedpalette.values())
        while True:
            new_color = (randrange(256), randrange(256), randrange(256))
            if new_color not in used_colors:
                return new_color

    def _process_palette(self):
        """
        Adjust palette to have the zeroth color set as transparent.
        Basically, get another palette index for the zeroth color.
        """
        self._set_parsed_palette()
        if 0 in self._img_p_used_palette_idxs:
            self._remap_palette_idx_zero()
        self._img_p_parsedpalette[0] = self._get_unused_color()

    def _adjust_pixels(self):
        'Convert the pixels into theire new values.'
        if self._palette_replaces['idx_from']:
            trans_table = bytearray.maketrans(
                bytes(self._palette_replaces['idx_from']),
                bytes(self._palette_replaces['idx_to']))
            self._img_p_data = self._img_p_data.translate(trans_table)
        for idx_pixel in self._transparent_pixels:
            self._img_p_data[idx_pixel] = 0
        self._img_p.frombytes(data=bytes(self._img_p_data))

    def _adjust_palette(self):
        'Modify the palette in the new `Image`.'
        unused_color = self._get_unused_color()
        final_palette = chain.from_iterable(
            self._img_p_parsedpalette.get(x, unused_color) for x in range(256))
        self._img_p.putpalette(data=final_palette)

    def process(self) -> Image:
        'Return the processed mode `P` `Image`.'
        self._img_p = self._img_rgba.convert(mode='P')
        self._process_pixels()
        if not self._transparent_pixels:
            return self._img_p
        self._img_p_data = bytearray(self._img_p.tobytes())
        self._palette_replaces = dict(idx_from=list(), idx_to=list())
        self._process_palette()
        self._adjust_pixels()
        self._adjust_palette()
        self._img_p.info['transparency'] = 0
        self._img_p.info['background'] = 0
        return self._img_p


def create_animated_gif(
    image: Image, size: tuple, do_watermark: bool = True,
) -> Tuple[Image, dict]:
    'If the image is a GIF, create an its thumbnail here.'
    save_kwargs = dict()

    def _thumbnails() -> Image:
        'Inner iterator for frames.'
        for idx, frame in enumerate(frames):  # type: int, Image
            thumbnail_rgba = frame.convert(mode='RGBA')
            if size != frame.size:
                thumbnail_rgba.thumbnail(size=size, reducing_gap=3.0)
            if do_watermark:
                thumbnail_rgba.paste(
                    im=WATERMARK_IMAGE, box=(0, 0), mask=WATERMARK_IMAGE)
            converter = TransparentAnimatedGifConverter(
                img_rgba=thumbnail_rgba)
            yield converter.process()  # type: Image

    frames = SeqIterator(im=image)
    output_image = next(_thumbnails())
    save_kwargs.update(
        format='GIF', save_all=True, optimize=False,
        append_images=list(_thumbnails()),
        disposal=2)  # Other disposals don't work
    return output_image, save_kwargs


def create_animated_webp(
    image: Image, size: tuple, do_watermark: bool = True
) -> Tuple[Image, dict]:
    'If the image is a WEBP, create an its thumbnail here.'
    save_kwargs = dict()
    frame_durations = list()

    def _thumbnails(index_size: Optional[Tuple[int, int]] = None) -> Image:
        'Inner iterator for frames.'
        for idx, frame in enumerate(frames):  # type: int, Image
            if index_size and frame.size != index_size:
                continue
            thumbnail_rgba = frame.convert(mode='RGBA')  # type: Image
            if size != frame.size:
                thumbnail_rgba.thumbnail(size=size, reducing_gap=3.0)
            thumbnail_rgba.save(f'{idx}.webp', format='WEBP')
            if do_watermark:
                thumbnail_rgba.paste(
                    im=WATERMARK_IMAGE, box=(0, 0), mask=WATERMARK_IMAGE)
            frame_durations.append(frame.info.get('duration', 1000))
            yield thumbnail_rgba

    frames = SeqIterator(im=image)
    output_image = next(_thumbnails())
    save_kwargs.update(
        format='WEBP', allow_mixed=True,
        background=output_image.info.get('background', (0, 0, 0, 0)))
    append_images = list(_thumbnails(index_size=output_image.size))
    if append_images:
        save_kwargs.update(
            save_all=True, append_images=append_images,
            duration=frame_durations, loop=output_image.info.get('loop', True))
    return output_image, save_kwargs


def get_converted_image(image: Image) -> Image:
    'Return an `Image` converted to a format that can be worked with.'
    converted_format = CONVERSION_MAP.get(image.format, 'RGBA')
    if image.format == converted_format:
        return image.copy()
    return image.convert(mode=converted_format)


def convert_image(
    image: Image, size: Tuple[int, int], do_watermark: bool = True
) -> Tuple[Image, dict]:
    """
    Return the converted image and its keyword arguments for saving.
    This is an umbrella function for converting images properly.
    """
    if image.format == 'GIF':
        image, save_kwargs = create_animated_gif(
            image=image, size=size, do_watermark=do_watermark)
    elif image.format == 'WEBP':
        image, save_kwargs = create_animated_webp(
            image=image, size=size, do_watermark=do_watermark)
    else:
        save_kwargs = dict()
        image = get_converted_image(image=image)
        if image.size != size:
            image.thumbnail(size=size, reducing_gap=3.0)
        if do_watermark:
            image.paste(im=WATERMARK_IMAGE, box=(0, 0), mask=WATERMARK_IMAGE)
    return image, save_kwargs
