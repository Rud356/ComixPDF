import pathlib
import atexit
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache

from PIL import Image

from config import config


@dataclass
class ComixImage:
    path: pathlib.Path
    _position: int
    included: bool = True

    image: Image = None

    def __post_init__(self):
        self._open_image()
        atexit.register(self.__del__)

    def _open_image(self):
        try:
            self.image = Image.open(self.path)

        except (FileNotFoundError, Image.UnidentifiedImageError):
            raise ValueError("Invalid image path")

    @property
    def name(self) -> str:
        return self.path.stem

    @property
    def modification_timestamp(self) -> float:
        return self.path.lstat().st_mtime

    @property
    def position(self) -> int:
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    def thumbnail(self, size=config.thumbnails_size) -> Image:
        thumbnail = deepcopy(self.image)
        thumbnail.thumbnail(size)

        return thumbnail

    def convert(self):
        size = [res + config.borders_size*2 for res in self.image.size]
        new_img = Image.new('RGB', size, (255, 255, 255))

        try:
            new_img.paste(self.image, mask=self.image.split()[3], box=[config.borders_size]*4)
            self.image = new_img

        finally:
            return self.image

    def __str__(self):
        return f"{self.position}. {self.name} | {self.path}"

    def __del__(self):
        self.image = None
