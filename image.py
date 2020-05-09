import imghdr
import pathlib
import numpy as np

from PIL import Image
from PIL.ImageQt import ImageQt

ALLOWED_FORMATS = {
    'jpeg', 'rgb', 'gif',
}
# Thumbnails size
T_SIZE = (512, 512)

class CMXImage:
    def __init__(self, path: pathlib.Path):
        self.path: pathlib.Path = path
        self.image = Image.open(path)
        self._thumbnail = None
        # -1 stands for dequeued
        self._position = -1

    @property
    def name(self):
        return self.path.stem

    @property
    def modified_date(self):
        return self.path.lstat().st_mtime

    @property
    def thumbnail(self):
        if not self._thumbnail:
            self._thumbnail = Image.open(self.path)
            self._thumbnail.thumbnail(T_SIZE)

        return self._thumbnail

    @property
    def ConvertedImage(self):
        new_img = Image.new('RGB', self.image.size, (255, 255, 255))
        try:
            new_img.paste(self.image, mask=self.image.split()[3])
            self.image = new_img

        finally:
            return self.image

    @property
    def QThumbnail(self):
        thumbnail = self.thumbnail
        return ImageQt(thumbnail)

    @property
    def QImage(self):
        image = self.image
        return ImageQt(image)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
