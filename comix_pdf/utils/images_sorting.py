"""
Some functions for sorting images inside of Comics list.
"""

from comix_pdf.types.image import ComicsImage


def order_image_by_modification_timestamp(image: ComicsImage) -> float:
    return image.modification_timestamp


def order_image_by_filename(image: ComicsImage) -> str:
    return image.path.name
