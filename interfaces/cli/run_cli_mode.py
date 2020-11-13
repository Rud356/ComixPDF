import os
import sys
import atexit
from math import ceil
from time import sleep
from enum import Enum

from modules import logging_setup
from custom_types.comix import ComixPDF
from custom_types.image import ComixImage

# TODO: add translations
# Below listed sleep delays to switch contexts and etc.
# Should be about right fast enough to read text
QUICK_LEAVE = 0.43
NOTICE_BEFORE_LEAVE = 0.5
READ_BEFORE_LEAVE = 0.765

IMAGES_PER_PAGE = 5


def clear():
    os.system('cls') if os.name == 'nt' else os.system('clear')


def unknown_command():
    print("Sorry, but there's no such command")
    sleep(READ_BEFORE_LEAVE)


def goodbye():
    clear()
    print("See you soon and good luck!")
    sleep(QUICK_LEAVE)


def exclude_keys(*keys, _dict: dict):
    return {k: v for k, v in _dict.items() if k not in keys}


class Context(Enum):
    start = 0
    image_manager = 1
    image_selected = 2


class CLI:
    def __init__(self):
        self.run = True
        self.comix: ComixPDF = None
        self.context: Context = Context.start

        self.images_page = 0
        self.selected_image_position: int = 0
        atexit.register(goodbye)

    def run_render(self):
        clear()

        while self.run:
            print('Welcome to ComixPDF 2.0! Created by @Rud356')
            print('Type x to exit program')
            self.render_cli()
            clear()

    def render_cli(self):
        if self.context == Context.start:
            self.start_context()

        elif self.context == Context.image_manager:
            self.image_manager()

        elif self.context == Context.image_selected:
            self.image_selected()

        else:
            print("How the hell you got there?")

    def start_context(self):
        class StartContextFunctions:
            @staticmethod
            def load_comix():
                nonlocal self
                path = input("input comics path: ")

                try:
                    self.comix = ComixPDF(path)

                except ComixPDF.exc.InvalidPath:
                    print("Entered path is not a directory")
                    sleep(NOTICE_BEFORE_LEAVE)

            @staticmethod
            def set_name():
                nonlocal self
                name = input("input comics title: ")
                try:
                    self.comix.title = name

                except ValueError:
                    print("Too big comics title, please try again")
                    sleep(NOTICE_BEFORE_LEAVE)

            @staticmethod
            def to_image_manager():
                nonlocal self
                self.context = Context.image_manager

                print("Moving to image manager")
                sleep(QUICK_LEAVE)

            @staticmethod
            def set_output_path():
                nonlocal self
                path = input("input pdf output path: ")

                try:
                    self.comix.output_path = path

                except ComixPDF.exc.InvalidPath:
                    print("Entered path is not a directory")
                    sleep(NOTICE_BEFORE_LEAVE)

            @staticmethod
            def render_comix():
                nonlocal self
                print("Please, be patient and wait until the job is done")
                self.comix.render()

                print("Done!")
                sleep(QUICK_LEAVE)

        options = {
            "1": StartContextFunctions.load_comix,
            "2": StartContextFunctions.set_name,
            "3": StartContextFunctions.to_image_manager,
            "4": StartContextFunctions.set_output_path,
            "5": StartContextFunctions.render_comix,
            "x": lambda: lambda: sys.exit(0)
        }

        is_comix_loaded = 'yes' if self.comix else 'no'
        comix_title = self.comix.title if self.comix else 'None'
        comix_path = self.comix.output_path if self.comix else 'None'

        print(
            f"Comics is loaded: {is_comix_loaded}",
            f"Comics name: {comix_title}",
            f"Comics path: {comix_path}",
            "1) Load comix from folder",
            sep='\n'
        )

        if self.comix:
            print(
                "2) Set title",
                "3) Image manager",
                "4) Set output path",
                "5) Render comics",
                sep='\n'
            )

        else:
            options = exclude_keys('2', '3', '4', '5', _dict=options)

        selected_option = input("Choose option: ")
        func = options.get(selected_option, unknown_command)
        func()

    def image_manager(self):
        class ImageManagerContextFunctions:
            @staticmethod
            def to_main_menu():
                nonlocal self
                self.context = Context.start

                print("Moving to main menu")
                sleep(QUICK_LEAVE)

            @staticmethod
            def sort_by_image_names():
                nonlocal self
                self.comix.set_sorting_mode("title_key")

            @staticmethod
            def sort_by_image_modifications_dates():
                nonlocal self
                self.comix.set_sorting_mode("modification_timestamp_key")

            @staticmethod
            def reverse_sorting():
                nonlocal self
                self.comix.sorting_reverse = not self.comix.sorting_reverse

            @staticmethod
            def select_image():
                nonlocal self
                try:
                    image_pick = int(input("select image: "))

                except ValueError:
                    print("Please, input index of image you want to pick")
                    sleep(QUICK_LEAVE)
                    return

                if image_pick not in range(len(self.comix.images)):
                    print("Please, input valid index of image")
                    sleep(QUICK_LEAVE)
                    return

                self.selected_image_position = image_pick
                self.context = Context.image_selected

                print("Going to selected image!")
                sleep(QUICK_LEAVE)

            @staticmethod
            def change_page():
                nonlocal self
                pages_count = self.pages_count

                try:
                    page = int(input("Type page number: ")) - 1

                    if page not in range(pages_count):
                        print("Please, input pages in given range")
                        sleep(QUICK_LEAVE)

                except ValueError:
                    print("Please, input only integers")
                    sleep(QUICK_LEAVE)
                    return

                self.images_page = page

            @staticmethod
            def next_page():
                nonlocal self
                pages_count = self.pages_count
                page = self.images_page + 1

                if page not in range(pages_count):
                    self.images_page = 0
                    return

                self.images_page = page

            @staticmethod
            def previous_page():
                nonlocal self
                pages_count = self.pages_count
                page = self.images_page - 1

                if page not in range(pages_count):
                    self.images_page = 0
                    return

                self.images_page = page

        options = {
            "1": ImageManagerContextFunctions.to_main_menu,
            "2": ImageManagerContextFunctions.sort_by_image_names,
            "3": ImageManagerContextFunctions.sort_by_image_modifications_dates,
            "4": ImageManagerContextFunctions.reverse_sorting,
            "5": ImageManagerContextFunctions.select_image,
            "6": ImageManagerContextFunctions.change_page,
            ">": ImageManagerContextFunctions.next_page,
            "<": ImageManagerContextFunctions.previous_page,
            "x": lambda: sys.exit(0)
        }

        print(
            "1) Go to main menu",
            "2) Sort images by names",
            "3) Sort images by modification date",
            "4) Reverse sorting",
            "5) Select image",
            "6) Select page",
            "<) previous page",
            ">) next page",
            sep='\n'
        )

        sorted_images = self.comix.all_images
        pages_offset = self.images_page*IMAGES_PER_PAGE

        print(f"pos   | is included? | {'image name':<40} | path")
        print(*sorted_images[pages_offset:pages_offset+IMAGES_PER_PAGE], sep='\n')
        print(f"Current position {self.images_page+1}/{self.pages_count}")

        option = options.get(input("Choose option: "), unknown_command)
        option()

    def image_selected(self):
        class ImageSelectedCommands:
            @staticmethod
            def show_image():
                cmx_image: ComixImage = self.comix.images[self.selected_image_position]
                cmx_image.image.show()

            @staticmethod
            def to_main_menu():
                self.context = Context.start

                print("Switching to main menu")
                sleep(QUICK_LEAVE)

            @staticmethod
            def to_image_manager():
                self.context = Context.image_manager

                print("Switching to image manager")
                sleep(QUICK_LEAVE)

            @staticmethod
            def switch_rendering_status():
                cmx_image: ComixImage = self.comix.images[self.selected_image_position]
                cmx_image.included = not cmx_image.included

        options = {
            "1": ImageSelectedCommands.to_image_manager,
            "2": ImageSelectedCommands.to_main_menu,
            "3": ImageSelectedCommands.switch_rendering_status,
            "4": ImageSelectedCommands.show_image,
            "x": lambda: sys.exit(0)
        }

        cmx_image: ComixImage = self.comix.images[self.selected_image_position]
        print(f"Selected image:\n  > {cmx_image.name}\n  > {cmx_image.path}")
        print(
            "1) Go back to image manager",
            "2) Go back to main menu",
            f"3) {'Exclude' if cmx_image.included else 'Include'} image to final pdf file",
            "4) Show image",
            sep='\n'
        )

        option = options.get(input("Choose option: "), unknown_command)
        option()

    @property
    def pages_count(self):
        return ceil(len(self.comix.images) / IMAGES_PER_PAGE)
