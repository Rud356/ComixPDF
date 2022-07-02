"""
Contains ComicsImages class that adds more functionality to Pil.Image.Image
class.
"""

from pathlib import Path

from PIL import Image

from .fill_color import FillColor


class ComicsImage(Image.Image):
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
        with Image.open(path) as _img:
            _img: Image.Image
            _img.verify()

    def convert_to_rgba(self) -> Image:
        """
        Returns copy of image in RGBA format.

        :return: Image instance with RGBA type.
        """
        return self.convert("RGBA")

    def convert_with_fill_color(
        self, fill_color: FillColor = FillColor(255, 255, 255)
    ) -> Image:
        """
        Returns copy of image in RGB format with background color
            set to fill_color.

        :param fill_color: sets a color for transparent background.
        :return: Image instance with RGBA type.
        """

        if self.mode == "RGBA":
            transparency = self.split()[3]
            new_img = Image.new('RGB', self.image.size, fill_color)
            new_img.paste(self, mask=transparency)
            return new_img

        else:
            return self.convert("RGB")

    def load_image(self) -> None:
        """
        Loads image from disk to memory.

        :return: nothing.
        """
        with open(self.path, "rb") as img:
            self.frombytes(img.read())

    @property
    def modification_timestamp(self) -> float:
        """
        When image was previously modified.

        :return: when image was modified last time in unix time format.
        """
        return self.path.lstat().st_mtime
