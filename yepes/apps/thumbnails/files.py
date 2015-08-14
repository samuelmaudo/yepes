# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from base64 import b64encode
from hashlib import md5
import os

from wand.image import Image

from django.core.files.base import ContentFile, File
from django.core.files.storage import default_storage
from django.db.models.fields.files import FieldFile
from django.utils import timezone
from django.utils.encoding import force_bytes

from yepes.apps.thumbnails.utils import clean_config
from yepes.loading import LazyModelManager
from yepes.types import Undefined

SourceManager = LazyModelManager('thumbnails', 'source')


class ImageFile(File):

    _format_cache = Undefined
    _height_cache = Undefined
    _image_cache = Undefined
    _width_cache = Undefined

    def _del_image(self, img):
        self._image_cache = Undefined
        self._format_cache = Undefined
        self._height_cache = Undefined
        self._width_cache = Undefined

    def _fetch_image_data(self):
        was_closed = self.closed
        if not was_closed:
            pos = self.tell()

        # By calling ``_get_image()``, properties are set.
        #
        # NOTE: Is not necessary to open or seek the file because
        #       ``_get_image()`` takes care of open it.
        #
        self._get_image()
        if was_closed:
            self.close()
        else:
            self.seek(pos)

    def _get_format(self):
        if self._format_cache is Undefined:
            self._fetch_image_data()
        return self._format_cache

    def _get_height(self):
        if self._height_cache is Undefined:
            self._fetch_image_data()
        return self._height_cache

    def _get_image(self):
        """
        Get an ImageMagick Image instance of this file.

        The image is cached to avoid the file needing to be read again if the
        function is called again.

        """
        try:
            self.open()  # Wand does not open the file before read it.
        except IOError:
            self._set_image(None)
        else:
            if self._image_cache is Undefined:
                self._set_image(Image(file=self))
        return self._image_cache

    def _get_width(self):
        if self._width_cache is Undefined:
            self._fetch_image_data()
        return self._width_cache

    def _set_image(self, img):
        """
        Set the image for this file.

        This also caches the dimensions and the format of the image.

        """
        if img is None:
            self._image_cache = None
            self._format_cache = None
            self._height_cache = None
            self._width_cache = None
        else:
            self._image_cache = img
            self._format_cache = img.format
            self._height_cache = img.height
            self._width_cache = img.width

    format = property(_get_format)
    height = property(_get_height)
    image = property(_get_image, _set_image, _del_image)
    width = property(_get_width)


class StoredImageFile(ImageFile):

    _file_cache = None

    def _del_file(self):
        self._file_cache = None

    def _get_accessed_time(self):
        return self.storage.accessed_time(self.name)

    def _get_closed(self):
        return (self._file_cache is None or self._file_cache.closed)

    def _get_created_time(self):
        return self.storage.created_time(self.name)

    def _get_file(self):
        if self._file_cache is None:
            self._file_cache = self.storage.open(self.name, 'rb')

        return self._file_cache

    def _get_modified_time(self):
        return self.storage.modified_time(self.name)

    def _get_path(self):
        return self.storage.path(self.name)

    def _get_size(self):
        if not self.closed:
            return self.file.size
        else:
            return self.storage.size(self.name)

    def _get_url(self):
        return self.storage.url(self.name)

    def _set_file(self, file):
        self._file_cache = file

    def close(self):
        if self._file_cache is not None:
            self._file_cache.close()

    def open(self, mode='rb'):
        self.file.open(mode)
    open.alters_data = True   # open() doesn't alter the file's contents,
                              # but it does reset the pointer

    accessed_time = property(_get_accessed_time)
    closed = property(_get_closed)
    created_time = property(_get_created_time)
    file = property(_get_file, _set_file, _del_file)
    modified_time = property(_get_modified_time)
    path = property(_get_path)
    size = property(_get_size)
    url = property(_get_url)


class SourceFile(StoredImageFile):
    """
    A file-like object which provides some methods to generate thumbnail images.
    """
    def __init__(self, file, name=None, storage=None, thumbnail_storage=None):
        super(SourceFile, self).__init__(file, name)
        self.storage = storage or default_storage
        self.thumbnail_storage = thumbnail_storage or self.storage

    def generate_thumbnail(self, config):
        """
        Generates a new thumbnail image and returns it as a ``ThumbnailFile``.
        """
        img = self.image
        if img is None:
            return None

        config = clean_config(config)
        thumb_name = self.get_thumbnail_name(config)
        with img.clone() as thumb:

            is_transparent = thumb.alpha_channel
            is_truecolor = ('truecolor' in thumb.type)

            # Set working format.
            thumb.format = 'MPC'
            if is_transparent:
                thumb.depth = 32
                thumb.type = 'truecolormatte'
            else:
                thumb.depth = 24
                thumb.type = 'truecolor'

            # Remove all image metadata, color profiles and comments included.
            thumb.strip()

            source_x = float(self.width)
            source_y = float(self.height)
            target_x = float(config.width)
            target_y = float(config.height)

            # Handle one-dimensional targets.
            if not target_x or not target_y:
                scale = max(target_x / source_x,
                            target_y / source_y)
            else:
                scale = min(target_x / source_x,
                            target_y / source_y)

            if scale < 1.0:
                # Resize the image to the target size boundary.
                # Round the scaled sizes to avoid floating point errors.
                x = int(round(source_x * scale))
                y = int(round(source_y * scale))
                if config.filter == 'sample':
                    thumb.sample(x, y)
                else:
                    thumb.resize(x, y, config.filter, config.blur)

            # Set final format.
            if is_truecolor:

                if is_transparent:
                    thumb.depth = 32
                    thumb.type = 'truecolormatte'
                    if config.format == 'WEBP':
                        thumb.format = 'WEBP'
                    else:
                        thumb.format = 'PNG'
                else:
                    thumb.depth = 24
                    thumb.type = 'truecolor'
                    if config.format == 'GIF':
                        thumb.format = 'JPEG'
                    else:
                        thumb.format = config.format

                if thumb.format in ('JPEG', 'WEBP'):
                    thumb.compression_quality = config.quality

            else:  # is_indexed

                thumb.depth = 8
                if is_transparent:
                    thumb.type = 'palettematte'
                else:
                    thumb.type = 'palette'

                if config.format == 'JPEG':
                    thumb.format = 'PNG'
                else:
                    thumb.format = config.format

            # Transform larger jpeg images (those more than 10KB in size)
            # into progressive jpegs.
            # Large progressive jpegs generally compress better and permit
            # incremental display by the browser.
            thumb_blob = thumb.make_blob()
            if (thumb.format == 'JPEG'
                    and len(thumb_blob) > 10 * 1024):
                thumb.format = 'PJPEG'
                thumb_blob = thumb.make_blob()

            thumb_file = ContentFile(thumb_blob)
            try:
                self.thumbnail_storage.delete(thumb_name)
            except Exception:
                pass
            self.thumbnail_storage.save(thumb_name, thumb_file)

        return ThumbnailFile(thumb_name, thumb_file, self.thumbnail_storage)

    def get_existing_thumbnail(self, config):
        """
        Returns a ``ThumbnailFile`` containing an existing thumbnail image.
        """
        thumb_name = self.get_thumbnail_name(config)
        if not thumb_name:
            return None

        try:
            thumb_modified_time = self.thumbnail_storage.modified_time(thumb_name)
        except Exception:
            return None

        if not thumb_modified_time:
            return None
        elif thumb_modified_time < self.modified_time:
            return None
        else:
            return ThumbnailFile(thumb_name, None, self.thumbnail_storage)

    def get_thumbnail(self, config):
        """
        Returns a ``ThumbnailFile`` containing a thumbnail.

        If a matching thumbnail already exists, it will simply be returned.
        Otherwise, a new thumbnail is generated.

        """
        config = clean_config(config)

        thumb = self.get_existing_thumbnail(config)
        if thumb is None:
            thumb = self.generate_thumbnail(config)

        return thumb

    def get_thumbnail_name(self, config):
        """
        Return the thumbnail filename for the given configuration.
        """
        img = self.image
        if img is None:
            return None

        config = clean_config(config)
        path, source_name = os.path.split(self.name)
        name = os.path.splitext(source_name)[0]

        # The key must identify the source and the configuration used to
        # generate the thumbnail. And must not contain any character that
        # is not allowed in a  filename.
        #
        # Use the configuration key is simpler but requires to maintain
        # the source extension and, more importantly, adds semantic value
        # to the original name.
        #
        key = '/'.join((config.key, source_name))
        key = md5(force_bytes(key)).digest()
        key = b64encode(key, b'ab').decode('ascii')[:6]

        if config.format != 'JPEG':
            extension = config.format.lower()
        elif 'truecolor' in img.type and not img.alpha_channel:
            extension = 'jpg'
        else:
            extension = 'png'

        thumb_name = '{0}_{1}.{2}'.format(name, key, extension)
        return os.path.join(path, 'thumbs', thumb_name)


class SourceFieldFile(FieldFile, SourceFile):

    _source_cache = Undefined

    def _get_source_record(self):
        if self._source_cache is Undefined:
            self._source_cache = SourceManager.filter(name=self.name).first()
        return self._source_cache

    def _get_thumbnail_records(self):
        source = self._get_source_record()
        if source is None:
            return []
        else:
            return source.thumbnails.all()

    def delete(self, *args, **kwargs):
        """
        Deletes the source image, along with any generated thumbnails.
        """
        self._set_image(None)

        source = self._get_source_record()
        self.delete_thumbnails()
        super(SourceFieldFile, self).delete(*args, **kwargs)
        if source is not None:
            source.delete()

    delete.alters_data = True

    def delete_thumbnails(self):
        """
        Deletes any thumbnails generated from this source image.
        """
        source = self._get_source_record()
        if source is None:
            return 0

        num_deleted = 0
        for record in self._get_thumbnail_records():
            try:
                self.thumbnail_storage.delete(record.name)
            except Exception:
                pass
            record.delete()
            num_deleted += 1

        return num_deleted
    delete_thumbnails.alters_data = True

    def generate_thumbnail(self, config):
        """
        Generates a new thumbnail image and returns it as a ``ThumbnailFile``.
        """
        thumb = super(SourceFieldFile, self).generate_thumbnail(config)
        if thumb is not None:
            source = self._get_source_record()
            if source is None:
                self.save(self.name, self)
                source = self._get_source_record()

            source.thumbnails.get_or_create(name=thumb.name)

        return thumb

    def get_thumbnails(self):
        """
        Returns an iterator which returns ``ThumbnailFile`` instances.
        """
        for record in self._get_thumbnail_records():
            yield ThumbnailFile(record.name, None, self.thumbnail_storage)

    def save(self, *args, **kwargs):
        """
        Saves the source file, also saving an instance of the ``Source`` model.
        """
        super(SourceFieldFile, self).save(*args, **kwargs)
        record, was_created = SourceManager.get_or_create(name=self.name)
        if not was_created:
            record.last_modified = timezone.now()
            record.save(update_fields=['last_modified'])

        self._source_cache = record


class ThumbnailFile(StoredImageFile):
    """
    A thumbnailed file.
    """

    def __init__(self, name, file=None, storage=None):
        super(ThumbnailFile, self).__init__(file, name)
        self.storage = storage or default_storage

