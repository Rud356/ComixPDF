"""
Contains named tuple for storing RGB color values.
"""

from typing import NamedTuple


class FillColor(NamedTuple):
    """
    Type for storing RGB color that fills transparency for pdf output.
    """

    Red: int
    Blue: int
    Green: int
