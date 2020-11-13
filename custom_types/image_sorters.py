from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .image import ComixImage


class ImageSorterKeys:
    @staticmethod
    def position_key(image: ComixImage):
        # If image is excluded from render - we move it
        # to the bottom of list
        is_not_excluded = not image.included
        return is_not_excluded, image.position

    @staticmethod
    def modification_timestamp_key(image: ComixImage):
        # If image is excluded from render - we move it
        # to the bottom of list
        is_not_excluded = not image.included
        return is_not_excluded, image.modification_timestamp

    @staticmethod
    def title_key(image: ComixImage):
        # If image is excluded from render - we move it
        # to the bottom of list
        is_not_excluded = not image.included
        return is_not_excluded, image.name
