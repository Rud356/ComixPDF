from typing import List, NamedTuple

from .image import ComicsImage


class ExcludedImage(NamedTuple):
    image: ComicsImage
    previous_position_index: int


class ExcludedImages(list, List[ExcludedImage]):
    def append(self, excluded_image: ExcludedImage) -> None:
        super().append(excluded_image)
