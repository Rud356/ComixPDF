import argparse
from pathlib import Path

from PIL import UnidentifiedImageError

from comix_pdf import __version__
from comix_pdf.types import Comics, ComicsImage

parser = argparse.ArgumentParser(
    description=f"ComixPDF (pip release version {__version__})."
)
parser.add_argument(
    "--title",
    "-t", type=str,
    action="store",
    default=None,
    dest="title",
    help="Sets a title for outputted pdf file"
)
parser.add_argument(
    "--paths",
    "-p", type=str,
    default=[],
    nargs="*",
    action="store",
    dest="parts_paths",
    help="Pass here directories or some images paths you would like insert"
    "in that exact order"
)
parser.add_argument(
    "--output-dir",
    "-od", type=str,
    default="./",
    action="store",
    dest="output_dir",
    help="which directory should be used for output"
)
parser.add_argument(
    "--quality",
    "-q", type=int,
    default=95,
    action="store",
    dest="quality",
    help="Sets images quality inside pdf"
)
parser.add_argument(
    "--resolution",
    "-res", type=int,
    default=95,
    action="store",
    dest="resolution",
    help="Sets printing quality (defaults to 300dpi)"
)


def inline_render(
    title: str,
    paths: list[str],
    output_directory: Path,
    quality: int,
    resolution: int
):
    comics = Comics(output_folder=output_directory, output_file_name=title)

    for path in paths:
        path: Path = Path(path)
        if path.is_dir():
            comics.append_from_folder(path)

        elif path.is_file():
            try:
                image: ComicsImage = ComicsImage(path)
                comics.append(image)

            except UnidentifiedImageError:
                # We delete object if file isn't image
                continue

    comics.render(quality, resolution)
    print(f"PDF file in: {comics.output_file_path}")

