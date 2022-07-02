"""
Possible custom exceptions are listed here.
"""


class NotAFolder(ValueError):
    """
    Errors related to path not being a folder.
    """


class OutputPathIsNotAFolder(NotAFolder):
    """
    Output directory path for comics isn't a folder.
    """


class InputPathIsNotAFolder(NotAFolder):
    """
    Input directory path for comics isn't a folder.
    """


class DirectoryHasNoImages(ValueError):
    """
    If input directory doesn't have any images this error is raised.
    """