import os
import sys
import argparse
from time import sleep
from comix import PComix
from enum import IntEnum

parser = argparse.ArgumentParser(description="It's CLI version of ComixPDF")
parser.add_argument('--path', '-p', type=str, action='store', dest='path')
parser.add_argument('--title', '-t', type=str, action='store', default='Undefined', dest='title')
parser.add_argument('--order_names', '-o_n', type=bool, dest='ordered_by_names', default=False)
parser.add_argument('--reverse', '-r', type=bool, dest='reverse', default=False)


def clear():
    if os.name == 'nt':
        os.system('CLS')
    else:
        os.system('clear')


class CLIContext(IntEnum):
    start = 0
    image_selection = 1
    image_selected = 2


class CLI:
    def __init__(self):
        self.run = True
        self._title = 'Untitled'
        self.Comix: PComix = None
        self.context = CLIContext.start

        self.reverse = False
        self.selected_image = 0

        while self.run:
            print('Welcome to ComixPDF 1.1! Created by @Rud356')
            print('Press x to close program')
            self.render_ui()
            clear()

        else:
            print('Goodbye!~ Hope I helped you')
            sleep(1.5)

    #? UI renderer
    def render_ui(self):
        if self.context == CLIContext.start:
            self.start_context()

        elif self.context == CLIContext.image_selection:
            self.image_selection_context()

        elif self.context == CLIContext.image_selected:
            self.image_selected_context()

        else:
            print(
                "Listen, I don't know how you got there, "
                "but if so - don't cry about something being broken"
            )

    def exit(self):
        self.run = False

    #? Contexts
    def start_context(self):
        options = {"1": self.load_comix, "x": self.exit}

        print(
            f'Comix loaded? - {self.Comix is not None}',
            f'Comix name: {self.title}',
            f'Comix path: {self.Comix.path if self.Comix is not None else None}',
            '1. Load comix folder',
            sep='\n'
        )

        if self.Comix:
            print(
                '2. Set comix name',
                '3. Sort by names',
                '4. Sort by dates',
                f'5. Reverse: {self.reverse}',
                '6. Images manager',
                '7. Render',
                sep='\n'
            )

            options.update({
                "2": self.set_title,
                "3": self.sorted_by_names,
                "4": self.sorted_by_dates,
                "5": self.change_reverse,
                "6": self.to_image_manager,
                "7": self.run_render,
            })

        selected = input("Your choice: ")
        func = options.get(selected, self.unknown_command)
        func()

    def image_selection_context(self):
        for n, image in enumerate(self.Comix.images, start=1):
            print(f'{n:<4} => {image.name:<25}')

        print(
            "1. Select image",
            "2. To main menu",
            "3. Sort by names",
            "4. Sort by dates",
            "5. Set position (Not working yet)",
            sep='\n'
        )

        options = {
            "x": self.exit,
            "1": self.to_selected_context,
            "2": self.to_main_menu,
            "3": self.sorted_by_names,
            "4": self.sorted_by_dates,
        }

        selected = input("Your choice: ")
        func = options.get(selected, self.unknown_command)
        func()

    def image_selected_context(self):
        if self.Comix.images[self.selected_image].position != -1:
            enable_or_disable = "Disable"

        else:
            enable_or_disable = "Enable"

        print(
            "1. Show image",
            "2. To main menu",
            "3. To image selection",
            f"4. {enable_or_disable} image from render",
            sep='\n'
        )

        options = {
            "x": self.exit,
            "1": self.Comix.images[self.selected_image].image.show,
            "2": self.to_main_menu,
            "3": self.to_image_manager,
            "4": self.enable_and_disable_image
        }

        selected = input("Your choice: ")
        func = options.get(selected, self.unknown_command)
        func()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if len(value) > 245:
            raise ValueError("Too long name")
        self.title = value

    #? If command isn't right
    def unknown_command(self):
        print("Sorry, but there's no such command")
        sleep(0.75)

    #? Context swithces
    def to_main_menu(self):
        self.context = CLIContext.start

    def to_image_manager(self):
        self.context = CLIContext.image_selection

    def to_selected_context(self):
        try:

            selected_image = int(input("Select image number: ")) - 1
            images_ids = len(self.Comix.images)
            if selected_image in range(images_ids):
                self.selected_image = selected_image
                self.context = CLIContext.image_selected

            else:
                print("Sorry, but your image number is invalid")
                sleep(0.55)

        except ValueError:
            print("Please, input only the integer values")
            sleep(0.65)

    #? Stuff for just making it work with dicts
    def change_reverse(self):
        self.reverse = not self.reverse

    def load_comix(self):
        path = input('path to comix folder here -> ')
        try:
            self.Comix = PComix.load_comix(path)

        except ValueError:
            print("Sorry, but you should input some folder path")
            sleep(0.65)

    def set_title(self):
        title = input("input comix title -> ")
        try:
            self.title = title

        except ValueError as ve:
            print(ve)
            sleep(0.65)

    def sorted_by_dates(self):
        self.Comix.sorted_by_names(self.reverse)

    def sorted_by_names(self):
        self.Comix.sorted_by_names(self.reverse)

    def run_render(self):
        if len(self.Comix.images):
            print("Sorry, but there's no images to render into pdf")
            sleep(0.65)
            return

        print("Starting render!")
        self.Comix.title = self.title
        self.Comix.render_pdf()
        print("Render finished!")
        sleep(0.45)

    def enable_and_disable_image(self):
        selected_image = self.Comix.images[self.selected_image]
        if selected_image.position != -1:
            selected_image.position = -1

        else:
            for n, image in enumerate(self.Comix.images):

                if image == selected_image:
                    selected_image.position = n
                    break


if len(sys.argv) == 1:
    CLI()

else:
    args = parser.parse_args()
    Comix = PComix.load_comix(args.path)
    Comix.title = args.title

    if args.ordered_by_names:
        Comix.sorted_by_names(args.reverse)

    else:
        Comix.sorted_by_dates(args.reverse)

    Comix.render_pdf()
