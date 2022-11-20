from os import system
from math import ceil
from pathlib import Path
from sys import exit
from typing import Optional, List

from PyInquirer import prompt, Separator, Validator, ValidationError
from transitions import Machine

from comix_pdf.types import Comics, ComicsImage, ExcludedImage
from .states import states

# How many images can be displayed on one page in menus
IMAGES_PER_PAGE = 8


class IntValidator(Validator):
    def validate(self, document):
        try:
            if document.text == "x":
                return

            int(document.text)

        except ValueError as exc:
            raise ValidationError(
                message="Only integer values accepted",
                cursor_position=len(document.text)
            ) from exc


class PercentageValidator(IntValidator):
    def validate(self, document):
        super(PercentageValidator, self).validate(document)
        if not 1 <= int(document.text) <= 100:
            raise ValidationError(
                message="Percentage must be between 1 and 100",
                cursor_position=len(document.text)
            )


class PrintingResolutionValidator(IntValidator):
    def validate(self, document):
        super().validate(document)
        if not 30 <= int(document.text) <= 1200:
            raise ValidationError(
                message="Percentage must be between 30 and 1200",
                cursor_position=len(document.text)
            )


class PathValidator(Validator):
    def validate(self, document):
        try:
            if document.text == "x":
                return

            f = Path(document.text)
            if not f.exists():
                raise ValueError(f"{f} doesn't exist")

        except ValueError as exc:
            raise ValidationError(
                message="Only existing paths accepted",
                cursor_position=len(document.text)
            ) from exc


def clear() -> None:
    """
    Clears console from text.

    :return: nothing.
    """
    print("\033[H\033[J", end="")


class ComixCLI:
    state: str
    comics: Optional[Comics]
    loaded_from_folder: Optional[Path]
    page: int
    total_pages: int
    sort_in_reverse: bool

    def __init__(self):
        # Maybe will add more translations
        self.resolution: int = 300
        self.quality: int = 90
        self.language = "en"
        self.sort_in_reverse = False
        self.page = 1
        self.total_pages = 0
        self.excluded_images_page = 1
        self.excluded_images_pages_total = 0
        self.machine = Machine(
            model=self, states=states, initial="start menu",
        )

        # Preparations to start main menu
        self.machine.add_transition(
            trigger="draw_start_menu", source="*", dest="start menu"
        )
        self.machine.add_transition(
            trigger="load_comics_menu", source="start menu",
            dest="load comics"
        )
        self.machine.add_transition(
            trigger="create_empty_comics", source="start menu",
            dest="empty comics created"
        )

        # Main menu transitions
        self.machine.add_transition(
            trigger="comics_loaded_menu", source=[
                "load comics",
                "empty comics created",
                "set output name",
                "set output path",
                "set printing resolution",
                "set images quality",
                "images manager",
                "rendering pdf",
            ],
            dest="loaded comics menu"
        )

        # Manipulations on main menu after comics is loaded
        self.machine.add_transition(
            trigger="set_comics_name", source="loaded comics menu",
            dest="set output name"
        )
        self.machine.add_transition(
            trigger="set_comics_name", source="loaded comics menu",
            dest="set output name"
        )
        self.machine.add_transition(
            trigger="set_printing_resolution", source="loaded comics menu",
            dest="set printing resolution"
        )
        self.machine.add_transition(
            trigger="set_images_quality", source="loaded comics menu",
            dest="set images quality"
        )
        self.machine.add_transition(
            trigger="image_manager_menu", source="loaded comics menu",
            dest="images manager"
        )
        self.machine.add_transition(
            trigger="render_comics", source="loaded comics menu",
            dest="rendering comics"
        )

        # Image manager states
        self.machine.add_transition(
            trigger="excluded_images", source="images manager",
            dest="excluded images"
        )
        self.machine.add_transition(
            trigger="select_image", source="images manager",
            dest="actions on image"
        )
        self.machine.add_transition(
            trigger="insert_images", source="images manager",
            dest="insert images"
        )

        # Start CLI
        self.output_start_menu()

    def output_start_menu(self):
        clear()
        print(
            "Welcome to ComixPDF! By @Rud356",
            "Current language is {self.language}",
            sep="\n"
        )

        start_menu = [
            {
                "type": "list",
                "name": "option",
                "message": (
                    "What action you want to do?"
                ),
                "choices": [
                    "Load comics from directory",
                    "Create empty comics",
                    "Exit"
                ]
            }
        ]

        answer = prompt(start_menu)

        if answer["option"] == "Exit":
            exit(0)

        if answer["option"] == "Load comics from directory":
            self.load_comics_menu()

        elif answer["option"] == "Create empty comics":
            self.create_empty_comics()

        else:
            raise ValueError(
                f"Unknown answer for state {self.state}: {answer}"
            )

    def load_comics_menu(self):
        load_menu = [
            {
                "type": "input",
                "name": "comics_path",
                "message":
                    'To close this menu type "x"\n'
                    "Input path form where to load pictures:",
                "validate": PathValidator
            }
        ]
        path_input = prompt(load_menu)
        path: Path = Path(path_input["comics_path"])

        while not path.is_dir():
            if path_input["comics_path"].lower() == "x":
                # Stopping function execution
                self.output_start_menu()
                return

            path: Path = Path(path_input["comics_path"])

            if path.is_dir():
                break

            else:
                load_menu = [
                    {
                        "type": "input",
                        "name": "comics_path",
                        "message":
                            "Previous input was not a path, which is required\n"
                            'To close this menu type "x"\n'
                            "Input path form where to load pictures:"
                    }
                ]
                path_input = prompt(load_menu)

        self.comics = Comics.load_from_folder(path)
        self.total_pages = ceil(len(self.comics) / IMAGES_PER_PAGE)
        self.comics_loaded_menu()

    def create_empty_comics(self):
        self.comics = Comics(
            output_folder=Path.cwd(),
            output_file_name="untitled.pdf"
        )
        self.comics_loaded_menu()

    def comics_loaded_menu(self):
        clear()
        print(
            'Current language is "{0}"'.format(self.language),
            "-- Information about loaded comics --",
            "Output file name: {0}".format(self.comics.output_file_name),
            "Output file path: {0}".format(self.comics.output_file_path),
            "Images included in final PDF: {0}".format(len(self.comics)),
            "Images excluded from final PDF: {0}".format(
                len(self.comics.excluded_images)
            ),
            "Images quality: {0}%".format(self.quality),
            "PDF printing resolution: {0}dpi\n".format(self.resolution),
            sep="\n"
        )
        loaded_comics_menu = [
            {
                "type": "list",
                "name": "option",
                "message": "Select action: ",
                "choices": [
                    Separator(" = Output settings = "),
                    "Set comics name",
                    "Set comics output path",
                    "Set images quality",
                    "Set printing resolution",
                    Separator(" = Comics management = "),
                    "Images manager",
                    "Render comics",
                    Separator(" = Finishing working = "),
                    "Close loaded comics",
                    "Exit"
                ]
            }
        ]
        answer = prompt(loaded_comics_menu)['option']

        if answer == "Set comics name":
            self.set_comics_name()

        elif answer == "Set comics output path":
            self.set_comics_output_path()

        elif answer == "Set images quality":
            self.set_images_quality()

        elif answer == "Set printing resolution":
            self.set_printing_resolution()

        elif answer == "Images manager":
            self.images_manager_menu()

        elif answer == "Render comics":
            self.render_comics()

        elif answer == "Close loaded comics":
            self.close_loaded_comics()

        elif answer == "Exit":
            exit(0)

        else:
            raise ValueError(f"Unknown answer: {answer}")

    def set_comics_name(self):
        comics_name_prompt = [
            {
                "type": "input",
                "name": "comics_name",
                "message":
                    'To close this menu type "x"\n'
                    "Set output file name:"
            }
        ]
        file_name_input = prompt(comics_name_prompt)
        if file_name_input["comics_name"] != "x":
            self.comics.output_file_name = file_name_input["comics_name"]

        self.comics_loaded_menu()

    def set_comics_output_path(self):
        output_comics_prompt = [
            {
                "type": "input",
                "name": "comics_path",
                "message":
                    'To close this menu - type "x"\n'
                    "Input path where comics will be saved:"
            }
        ]
        path_input = prompt(output_comics_prompt)

        while path_input["comics_path"].lower() != "x":
            path: Path = Path(path_input["comics_path"])

            if path.is_file():
                self.comics.output_file_name = path.name
                self.comics.output_file_path = path.parent
                break

            elif path.is_dir() and path != Path('.'):
                self.comics.output_folder = path
                break

            else:
                output_comics_prompt = [
                    {
                        "type": "input",
                        "name": "comics_path",
                        "message":
                            "Previous input was not a path, which is required\n"
                            'To close this menu type "x"\n'
                            "Input path where comics will be saved:"
                    }
                ]
                path_input = prompt(output_comics_prompt)

        self.comics_loaded_menu()

    def set_images_quality(self):
        input_image = [
            {
                "type": "input",
                "name": "image_quality",
                "message":
                    'Input "x" to close this menu\n'
                    "Input image quality which you would like (between 1 and 100):",
                "validate": PercentageValidator
            }
        ]
        answer: dict = prompt(input_image)
        if answer["image_quality"] == "x":
            self.comics_loaded_menu()
            return

        self.quality = int(answer["image_quality"])
        self.comics_loaded_menu()

    def set_printing_resolution(self):
        input_image = [
            {
                "type": "input",
                "name": "image_printing",
                "message":
                    'Input "x" to close this menu\n'
                    "Input image printing quality which you would like (between 30 and 1200):",
                "validate": PrintingResolutionValidator
            }
        ]
        answer: dict = prompt(input_image)
        if answer["image_printing"] == "x":
            self.comics_loaded_menu()
            return

        self.resolution = int(answer["image_printing"])
        self.comics_loaded_menu()

    def images_manager_menu(self):
        clear()
        # Text about what will be next state of sorting
        if not self.sort_in_reverse:
            setting_sorting_mode_to: str = 'reverse'
        else:
            setting_sorting_mode_to = 'normal'

        # Prepares page to be displayed in menu
        current_comics_displayed_pages = self.current_page
        images_page: list[str] = [
            f"{n}. {img.path.name}" for n, img in enumerate(
                current_comics_displayed_pages,
                start=1 + (self.page-1)*IMAGES_PER_PAGE
            )
        ]

        loaded_comics_menu = [
            {
                "type": "list",
                "name": "option",
                "message": "Select action with images: ",
                "choices": [
                    Separator(" = Images = "),
                    *images_page,
                    "Insert images",
                    "Excluded images",
                    Separator(" = Change page = "),
                    Separator(f"Current page: {self.page}"),
                    "Previous page",
                    "Next page",
                    Separator(" = Sorting = "),
                    "Sort by names",
                    "Sort by dates modified",
                    f"Change current sorting order to: {setting_sorting_mode_to}",
                    Separator(" = Return = "),
                    "Return to comics menu",
                    "Exit"
                ]
            }
        ]

        answer: str = prompt(loaded_comics_menu)["option"]

        if answer == "Previous page":
            # If we're still not on first page - we can go back
            if self.page > 1:
                self.page -= 1
            self.images_manager_menu()

        elif answer == "Next page":
            # If we still hadn't reached final page - it is fine
            if self.page < self.total_pages:
                self.page += 1
            self.images_manager_menu()

        elif answer == "Sort by names":
            self.comics.sort(
                reverse=self.sort_in_reverse,
                key=lambda img: img.name
            )
            self.images_manager_menu()

        elif answer == "Sort by dates modified":
            self.comics.sort(
                reverse=self.sort_in_reverse,
                key=lambda img: img.modification_timestamp
            )
            self.images_manager_menu()

        elif answer == "Return to comics menu":
            self.comics_loaded_menu()

        elif answer == "Excluded images":
            self.excluded_images()

        elif answer == "Exit":
            exit(0)

        elif answer == "Insert images":
            self.insert_images()

        elif answer.startswith("Change current sorting order to"):
            self.sort_in_reverse = not self.sort_in_reverse
            self.comics.reverse()
            self.images_manager_menu()

        elif answer.split(".")[0].isdecimal():
            image_index: int = int(answer.split(".")[0])
            self.select_image(image_index)

        else:
            raise ValueError(f"Unknown answer: {answer}")

    def select_image(self, image_index: int):
        image: ComicsImage = self.comics[image_index]
        while True:
            loaded_comics_menu = [
                {
                    "type": "list",
                    "name": "option",
                    "message": "Select action with images: ",
                    "choices": [
                        Separator(" = Info = "),
                        Separator(f"Image index: {image_index}"),
                        Separator(f"Image name: {image.name}"),
                        # TODO: add info about if it's excluded
                        Separator(" = Image actions = "),
                        "Exclude image", # TODO: add isntant restore
                        "Show image",
                        Separator(" = Return = "),
                        "Return to images manager",
                        "Exit"
                    ]
                }
            ]
            answer: str = prompt(loaded_comics_menu)['option']

            if answer == "Return to images manager":
                self.images_manager_menu()

            elif answer == "Exit":
                exit(0)

            elif answer == "Show image":
                image._img.show() # noqa: need to show image

            elif answer == "Exclude image":
                self.comics.exclude_image_from_output(image_index)

            else:
                raise ValueError(f"Unknown answer: {answer}")

    @property
    def current_page(self) -> Comics[ComicsImage]:
        current_comics_page: Comics[ComicsImage] = self.comics[
            (self.page - 1) * IMAGES_PER_PAGE:self.page * IMAGES_PER_PAGE
        ]
        return current_comics_page

    @property
    def current_excluded_page(self) -> Comics[ComicsImage]:
        current_comics_page: Comics[ComicsImage] = self.comics.excluded_images[
            (self.excluded_images_page - 1) * IMAGES_PER_PAGE:
            self.excluded_images_page * IMAGES_PER_PAGE
        ]
        return current_comics_page

    def excluded_images(self):
        while True:
            images_page: list[ComicsImage] = self.current_excluded_page
            loaded_comics_menu = [
                {
                    "type": "list",
                    "name": "option",
                    "message": "Select action with images: ",
                    "choices": [
                        Separator(" = Images = "),
                        *[f"{original_index}. {img.name}\n" for img, original_index in images_page],
                        Separator(" = Change page = "),
                        Separator(f"Current page: {self.page}"),
                        "Previous page",
                        "Next page",
                        Separator(" = Return = "),
                        "Return to images menu",
                        "Exit"
                    ]
                }
            ]

            answer: str = prompt(loaded_comics_menu)['option']

            if answer == "Previous page":
                # If we're still not on first page - we can go back
                if self.page > 1:
                    self.page -= 1
                self.excluded_images()

            elif answer == "Next page":
                # If we still hadn't reached final page - it is fine
                if self.page < self.total_pages:
                    self.page += 1
                self.excluded_images()

            elif answer == "Return to images menu":
                self.images_manager_menu()

            elif answer == "Excluded images":
                self.excluded_images()

            elif answer == "Exit":
                exit(0)

            elif answer.split(".")[0].isdecimal():
                image_index: int = int(answer.split(".")[0]) - 1
                excluded_image: ExcludedImage = self.comics.excluded_images[image_index]

                while True:
                    loaded_comics_menu = [
                        {
                            "type": "list",
                            "name": "option",
                            "message": "Select action with images: ",
                            "choices": [
                                Separator(" = Info = "),
                                Separator(f"Image index: {image_index+1}"),
                                Separator(f"Image name: {excluded_image.image.name}"),
                                Separator(" = Image actions = "),
                                "Restore image",
                                "Show image",
                                Separator(" = Return = "),
                                "Return to excluded images manager",
                                "Exit"
                            ]
                        }
                    ]
                    answer: str = prompt(loaded_comics_menu)['option']

                    if answer == "Return to excluded images manager":
                        break

                    elif answer == "Exit":
                        exit(0)

                    elif answer == "Show image":
                        excluded_image._img.show()  # noqa: need to show image

                    elif answer == "Restore image":
                        self.comics.restore_image_from_excluded(image_index)
                        break

                    else:
                        raise ValueError(f"Unknown answer: {answer}")

    def insert_images(self):
        try:
            image, index = self.require_image_insertion_input()
            self.comics.insert_image(image, index)

        except ValueError:
            self.images_manager_menu()
            return

    def render_comics(self):
        self.comics.render(self.quality, self.resolution)

    def close_loaded_comics(self):
        del self.comics
        self.output_start_menu()

    def require_image_insertion_input(self) -> (ComicsImage, int):
        input_image = [
            {
                "type": "input",
                "name": "image_path",
                "message":
                    'To close this menu - type "x"\n'
                    "Input path form where to load picture:",
                "validate": PathValidator
            },
            {
                "type": "input",
                "name": "image_index",
                "message":
                    "Input index to which you wish insert image:",
                "validate": IntValidator
            }
        ]
        answer: dict = prompt(input_image)
        if answer["image_path"] == "x" or answer["image_index"] == "x":
            raise ValueError("Must return to previous menu")

        image: ComicsImage = ComicsImage(answer["image_path"])
        image_index: int = int(answer["image_index"])

        return image, image_index
