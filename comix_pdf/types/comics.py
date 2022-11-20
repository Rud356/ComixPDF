"""
This module contains Comics class that is used to store ComicsImages that
needs to be rendered and contains methods for manipulating where and how images
are placed in files pages.
"""

import textwrap
from copy import copy
from pathlib import Path
from typing import List, Optional
from PIL import Image, UnidentifiedImageError

from pathvalidate import sanitize_filename
from comix_pdf import exceptions
from .excluded_images import ExcludedImage, ExcludedImages
from .image import ComicsImage
from .fill_color import FillColor


class Comics(list, List[ComicsImage]):
    def __init__(
        self,
        output_folder: Path,
        output_file_name: str,
        *args, **kwargs
    ):
        if not output_folder.is_dir():
            raise exceptions.OutputPathIsNotAFolder(
                "Output folder must be directory"
            )

        self._output_folder: Path = output_folder
        self._output_file_name: str = "untitled.pdf"

        self.output_file_name = output_file_name
        self.excluded_images = ExcludedImages()
        super().__init__(*args, **kwargs)

    def move_image(self, from_index: int, to_index: int) -> None:
        """
        Moves image from one index to another.

        :param from_index: from where we take image.
        :param to_index: where we place image.
        :return: nothing.
        :raises IndexError: if supplied image to move from index is out of
        range.
        """
        if from_index not in range(0, len(self)):
            raise IndexError("Image for being moved is out of reach")

        self.insert(
            to_index,
            self.pop(from_index)
        )

    def exclude_image_from_output(self, image_index: int) -> None:
        """
        Excludes image on index from rendering to pdf.

        :param image_index: image index inside of comics list.
        :return: nothing.
        :raises IndexError: if supplied image index is out of range.
        """
        if image_index not in range(0, len(self)):
            raise IndexError("Image for exclusion is out of reach")

        excluded_image: ExcludedImage = ExcludedImage(
            self.pop(image_index),
            image_index
        )
        self.excluded_images.append(excluded_image)

    def restore_image_from_excluded(
        self, excluded_image_index: int,
        restore_to_index: Optional[int] = None
    ) -> None:
        """
        Brings image back to output.

        :param excluded_image_index: index of excluded image inside
            excluded_images parameter.
        :param restore_to_index: where to put restored image. By default
        restores image to previous index (shifts images after its index by +1).
        :return: nothing.
        :raises IndexError: if supplied image index inside of excluded images
            is out of range.
        """
        if excluded_image_index not in range(0, len(self.excluded_images)):
            raise IndexError(
                "Image for restoration is out of reach in excluded images list"
            )

        excluded_image: ExcludedImage = self.excluded_images.pop(
            excluded_image_index
        )
        if restore_to_index is None:
            restore_to_index = excluded_image.previous_position_index

        self.insert(restore_to_index, excluded_image.image)

    def insert_image(
        self, image: ComicsImage, to_index: Optional[int] = None
    ) -> None:
        """
        Inserts an image into comics from any place.

        :param image: ComicsImage instance to be inserted.
        :param to_index: where to put the image. By default
        puts image at the end.
        :return: nothing.
        """
        if to_index is None:
            to_index = len(self)

        self.insert(to_index, image)

    def render(
        self, quality: int = 90, resolution: int = 300,
        fill_color: Optional[FillColor] = None
    ) -> None:
        """
        Renders the comics into PDF file.

        :param quality: the quality of images to be exported to pdf.
        :param resolution: DPI resolution that will be used when printing.
        :param fill_color: by default outputs images with transparent
        background. If it needs to be filled with color - set fill_color
        parameter.
        :return: nothing.
        """
        images_render_queue: Comics = copy(self)
        converted_images: List[Image.Image] = []

        for image in images_render_queue:
            if fill_color is None:
                converted_image: Image.Image = image.convert_to_rgb()
            else:
                converted_image = image.convert_to_rgb_with_fill_color(
                    fill_color
                )

            converted_images.append(converted_image)

        if len(converted_images) == 0:
            raise ValueError("No images to render as PDF")

        converted_images[0].save(
            self.output_file_path, "PDF", optimized=True,
            quality=quality, resolution=resolution, save_all=True,
            append_images=converted_images[1:],
            **converted_images[0].info
        )

        del converted_images
        del images_render_queue

    @classmethod
    def load_from_folder(cls, folder: Path) -> 'Comics':
        """
        Creates comics from provided folder.

        :param folder: folder which will be used to output pdf,
        and to collect images from it. Also uses folder name as default output
        file name.
        :return: Instance of Comics.
        """
        output_file_name: str = textwrap.shorten(
            folder.name, width=251, placeholder=""
        )
        output_file_name = f"{output_file_name}.pdf"

        comics = cls(folder, output_file_name)
        comics.append_from_folder(folder)

        return comics

    def append_from_folder(self, folder: Path) -> None:
        if not folder.is_dir():
            raise exceptions.InputPathIsNotAFolder(
                f"{folder} isn't a folder"
            )

        found_images: int = 0
        for filepath in filter(lambda f: f.is_file(), folder.iterdir()):
            try:
                image: ComicsImage = ComicsImage(filepath)

            except UnidentifiedImageError:
                # We delete object if file isn't image
                continue

            self.append(image)
            found_images += 1

        if not found_images:
            raise exceptions.DirectoryHasNoImages(f"{folder} has no images")

    @property
    def output_file_name(self) -> str:
        return self._output_file_name

    @output_file_name.setter
    def output_file_name(self, value: str) -> None:
        value = sanitize_filename(value)
        if value == "":
            value = "Untitled"

        output_file_name: str = textwrap.shorten(
            value, width=251, placeholder=""
        )
        if not output_file_name.endswith(".pdf"):
            self._output_file_name = f"{output_file_name}.pdf"

        else:
            self._output_file_name = output_file_name

    @property
    def output_folder(self) -> Path:
        return self._output_folder

    @output_folder.setter
    def output_folder(self, value: Path) -> None:
        if not value.is_dir():
            raise exceptions.OutputPathIsNotAFolder(
                "Output folder must be directory"
            )

        self._output_folder = value

    @property
    def output_file_path(self) -> Path:
        return self.output_folder / self.output_file_name
