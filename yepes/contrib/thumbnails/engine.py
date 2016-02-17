# -*- coding:utf-8 -*-

from __future__ import division, unicode_literals


def calculate_measures(source, config):
    if config.mode in ('scale', 'fit', 'limit', 'fill', 'lfill', 'pad', 'lpad'):

        if not config.width:
            scale = config.height / source.height
            if config.mode.startswith('l'):
                scale = min(scale, 1)

            canvas_width = image_width = source.width * scale
            canvas_height = image_height = config.height

        elif not config.height:
            scale = config.width / source.width
            if config.mode.startswith('l'):
                scale = min(scale, 1)

            canvas_width = image_width = config.width
            canvas_height = image_height = source.height * scale

        elif config.mode == 'scale':
            canvas_width = image_width = config.width
            canvas_height = image_height = config.height

        elif config.mode in ('fit', 'limit'):
            scale = min(
                config.width / source.width,
                config.height / source.height,
            )
            if config.mode == 'limit':
                scale = min(scale, 1)

            canvas_width = image_width = source.width * scale
            canvas_height = image_height = source.height * scale

        elif config.mode in ('fill', 'lfill'):
            scale = max(
                config.width / source.width,
                config.height / source.height,
            )
            if config.mode == 'lfill':
                scale = min(scale, 1)

            canvas_width = config.width
            canvas_height = config.height
            image_width = source.width * scale
            image_height = source.height * scale

        elif config.mode in ('pad', 'lpad'):
            scale = min(
                config.width / source.width,
                config.height / source.height,
            )
            if config.mode == 'lpad':
                scale = min(scale, 1)

            canvas_width = config.width
            canvas_height = config.height
            image_width = source.width * scale
            image_height = source.height * scale

    elif config.mode == 'crop':
        if not config.width:
            canvas_width = source.width
            canvas_height = config.height
        elif not config.height:
            canvas_width = config.width
            canvas_height = source.height
        else:
            canvas_width = config.width
            canvas_height = config.height

        image_width = source.width
        image_height = source.height

    else:
        raise ValueError

    canvas_width = int(round(canvas_width))
    canvas_height = int(round(canvas_height))
    image_width = int(round(image_width))
    image_height = int(round(image_height))
    return canvas_width, canvas_height, image_width, image_height


def calculate_position(canvas, image, config):
    if config.gravity == 'north_west':
        left = 0
        top = 0
    elif config.gravity == 'north':
        left = (canvas.width - image.width) / 2
        top = 0
    elif config.gravity == 'north_east':
        left = canvas.width - image.width
        top = 0
    elif config.gravity == 'west':
        left = 0
        top = (canvas.height - image.height) / 2
    elif config.gravity == 'center':
        left = (canvas.width - image.width) / 2
        top = (canvas.height - image.height) / 2
    elif config.gravity == 'east':
        left = canvas.width - image.width
        top = (canvas.height - image.height) / 2
    elif config.gravity == 'south_west':
        left = 0
        top = canvas.height - image.height
    elif config.gravity == 'south':
        left = (canvas.width - image.width) / 2
        top = canvas.height - image.height
    elif config.gravity == 'south_east':
        left = canvas.width - image.width
        top = canvas.height - image.height
    else:
        raise ValueError

    left = int(round(left))
    top = int(round(top))
    return left, top


def composite_image(canvas, image, config):
    left, top = calculate_position(canvas, image, config)
    canvas.composite(image, left, top)
    return canvas


def get_format(config):
    if config.format == 'PNG64':
        # It is not always necessary to use 64 bits per pixel. This allows
        # ImageMagick to use a more economical format if it does not lose
        # information.
        return 'PNG'
    else:
        return config.format


def resize_image(image, target_width, target_height, config):
    if config.algorithm == 'sample':
        image.sample(target_width, target_height)
    else:
        lenght = max(target_width, target_height)
        scale = min(image.width / target_width,
                    image.height / target_height)

        if lenght <= 512 and scale > 7:
            # This increases resizing speed and produces good results for
            # small thumbnails.
            image.sample(target_width * 5, target_height * 5)

        if config.algorithm == 'liquid':
            image.liquid_rescale(target_width, target_height)
        else:
            image.resize(target_width, target_height, config.algorithm)

    return image

