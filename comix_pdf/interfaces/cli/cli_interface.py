from pathlib import Path
from sys import exit
from typing import Optional

from PyInquirer import prompt
from transitions import Machine

from comix_pdf.types import Comics
from .states import states


class ComixCLI:
    state: str
    comics: Optional[Comics]
    loaded_from_folder: Optional[Path]

    def __init__(self):
        # Maybe will add more translations
        self.resolution = 300
        self.quality = 90
        self.language = "en"

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

        # Start CLI
        self.draw_start_menu()

    def draw_start_menu(self):
        start_menu = [
            {
                "type": "list",
                "name": "option",
                "message": (
                    "Welcome to ComixPDF! By @Rud356\n"
                    "Current language is {self.language}\n"
                    "\nWhat action you want to do?"
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
                    "Input path form where to load pictures:"
            }
        ]
        path_input = prompt(load_menu)
        path: Path = Path(path_input["comics_path"])

        while not path.is_dir():
            if path_input["comics_path"].lower() == "x":
                # Stopping function execution
                self.draw_start_menu()
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
        self.comics_loaded_menu()

    def create_empty_comics(self):
        self.comics = Comics(
            output_folder=Path.cwd(),
            output_file_name="untitled.pdf"
        )
        self.comics_loaded_menu()

    def comics_loaded_menu(self):
        pass

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
            self.comics = file_name_input["comics_name"]

        self.comics_loaded_menu()

    def set_comics_output_path(self):
        output_comics_prompt = [
            {
                "type": "input",
                "name": "comics_path",
                "message":
                    'To close this menu - type "x"\n'
                    "Input path form where to load pictures:"
            }
        ]
        path_input = prompt(output_comics_prompt)

        while path_input["comics_path"].lower() != "x":
            path: Path = Path(path_input["comics_path"])

            if path.is_file():
                self.comics.output_file_name = path.name
                self.comics.output_file_path = path.parent
                break

            elif path.is_dir():
                self.comics.output_file_path = path
                break

            else:
                output_comics_prompt = [
                    {
                        "type": "input",
                        "name": "comics_path",
                        "message":
                            "Previous input was not a path, which is required\n"
                            'To close this menu type "x"\n'
                            "Input path form where to load pictures:"
                    }
                ]
                path_input = prompt(output_comics_prompt)

        else:
            self.comics_loaded_menu()

    def set_images_quality(self):
        self.comics_loaded_menu()

    def set_printing_resolution(self):
        self.comics_loaded_menu()

    def images_manager_menu(self):
        pass

    def close_loaded_comics(self):
        del self.comics
        self.draw_start_menu()
