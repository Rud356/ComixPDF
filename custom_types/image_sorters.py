from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .image import ComixImage


class ImageSorterKeys:
    @staticmethod
    def position_key(image: ComixImage):
        return image.position

    @staticmethod
    def modification_timestamp_key(image: ComixImage):
        return image.modification_timestamp

    @staticmethod
    def title_key(image: ComixImage):
        return image.name
