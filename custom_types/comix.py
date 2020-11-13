import atexit
import logging
import pathlib
from typing import List

from PIL import Image

from config import config
from .image import ComixImage
from .image_sorters import ImageSorterKeys


class ComixPDF:
    def __init__(self, comix_path: str):
        comix_path = pathlib.Path(comix_path)

        if not comix_path.is_dir():
            raise self.exc.InvalidPath("You've provided path that isn't a real directory")

        self._title = "untitled.pdf"
        self.sorting_reverse = config.reversed_sorting
        self.sorting_mode = config.default_sort_mode_
        self.initial_path: pathlib.Path = comix_path
        self._output_path: pathlib.Path = comix_path / self._title

        logging.info(f"{self.initial_path} is loaded comics dir")

        self.images: List[ComixImage] = []

        for comix_image in filter(lambda f: f.is_file(), comix_path.iterdir()):
            try:
                image = ComixImage(comix_image, len(self.images) + 1)
                self.images.append(image)

            except ValueError:
                pass

        logging.debug(
            f"{self.initial_path} images has been loaded from dir {len(self.images)}",
        )
        atexit.register(self.__del__)

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        if len(value) > 255:
            raise ValueError("Too long title for file")

        self._title = value
        if not self._title.endswith('.pdf') and len(self._title) < 251:
            self._title += '.pdf'

        self._output_path = self._output_path.parent / self._title
        logging.debug(f"{self._title} new title for comix at {self.initial_path}")

    @property
    def output_path(self) -> pathlib.Path:
        return self._output_path

    @output_path.setter
    def output_path(self, value):
        path = pathlib.Path(value)

        if path.is_dir():
            self._output_path = path / self._title

        elif path.parent.exists():
            self._output_path = path
            self._title = path.stem

        else:
            raise self.exc.InvalidPath("Invalid output path")

    @property
    def all_images(self):
        self.sort_pages()

        return self.images

    @property
    def listed_images(self):
        self.sort_pages()
        images: List[ComixImage] = list(filter(lambda img: img.included, self.images))

        return images

    @property
    def unlisted_images(self):
        self.sort_pages()
        unlisted = list(filter(lambda img: not img.included, self.images))

        return unlisted

    def update_positions(self):
        for n, page in enumerate(self.images):
            page.position = n

    def sort_pages(self):
        pages = self.images
        pages.sort(key=self.sorting_mode, reverse=self.sorting_reverse)
        self.update_positions()

    def set_sorting_mode(self, name: str):
        try:
            self.sorting_mode = getattr(ImageSorterKeys, name)

        except AttributeError:
            raise ValueError("Invalid sorting method name")

    def render(self):
        images: List[ComixImage] = self.listed_images

        if not len(images):
            raise ValueError("No images to render")

        first_page: Image = images.pop(0).convert()
        converted_images = [image.convert() for image in images]
        first_page_info = first_page.info

        first_page.save(
            self.output_path, 'PDF', optimized=config.optimized,
            quality=100, resolution=100, save_all=True,
            append_images=converted_images,
            **first_page_info
        )

    def __del__(self):
        del self

    class exc:
        class InvalidPath(ValueError):
            pass
