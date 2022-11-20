"""
Contains ComicsImages class that adds more functionality to Pil.Image.Image
class.
"""
from copy import copy
from pathlib import Path

from PIL import Image

from .fill_color import FillColor


class ComicsImage:
    """
    Type for image for comics' collection.
    """

    def __init__(self, path: Path):
        """
        Initializes custom Image object. To use object you first need to
        execute method load_image.

        :param path: where image is stored on disk.
        :raises PIL.UnidentifiedImageError: file is not an image.
        """
        super().__init__()
        self.path: Path = path

        # Validating that file is actually an image
        self._img: Image.Image = Image.open(path)
        copy(self._img).verify()

    def convert_to_rgb(self) -> Image:
        """
        Returns copy of image in RGBA format.

        :return: Image instance with RGBA type.
        """
        return self._img.convert("RGB")

    def convert_to_rgb_with_fill_color(
        self, fill_color: FillColor = FillColor(255, 255, 255)
    ) -> Image:
        """
        Returns copy of image in RGB format with background color
            set to fill_color.

        :param fill_color: sets a color for transparent background.
        :return: Image instance with RGBA type.
        """

        if self._img.mode == "RGBA":
            transparency = self._img.split()[3]
            new_img = Image.new('RGB', self._img.image.size, fill_color)
            new_img.paste(self, mask=transparency)
            return new_img

        else:
            return self.convert_to_rgb()

    @property
    def modification_timestamp(self) -> float:
        """
        When image was previously modified.

        :return: when image was modified last time in unix time format.
        """
        return self.path.lstat().st_mtime

    @property
    def name(self) -> str:
        return self.path.name
