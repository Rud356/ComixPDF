import os
import pathlib
from PIL import Image
from enum import Enum
from time import sleep
opened_files = []


class Context(Enum):
    load_pages = 1
    image_selection = 2
    image_selected = 3


class PImage:
    def __init__(self, date, img, position, filename):
        self.filename = filename
        self.position = position
        self.date = date
        self.img = img

    @classmethod
    def load(cls, path, position):
        try:
            name = pathlib.Path(path).stem
            f = open(path, 'rb')
            opened_files.append(f)
            img = Image.open(f)
            date = os.path.getmtime(path)
            return cls(date, img, position, name)
        except Exception as e:
            print(e)

    @staticmethod
    def sorter_date(p_image):
        return p_image.date

    @staticmethod
    def sorted_names(p_image):
        return p_image.filename

    @staticmethod
    def sorted_pos(p_image):
        return p_image.position

    def show(self):
        self.img.show()


class PComix:
    def __init__(self, path):
        if os.path.isdir(path):
            self.path = path

        else:
            raise ValueError(f'Comix path must be correct dir; `{path}`')

        self.images = []
        img_paths = pathlib.Path(path).iterdir()
        for n, img in enumerate(img_paths):
            if not os.path.isfile(img):
                continue

            loaded_img = PImage.load(img, n)
            self.images.append(loaded_img)

    def image_list(self):
        return self.images

    def sort_names(self):
        self.images.sort(key=PImage.sorted_names)

    def sort_time(self):
        self.images.sort(key=PImage.sorter_date)

    def sort_position(self):
        self.images.sort(key=PImage.position)

    def create_pdf(self, name, manual_sort=False):
        _images: PImage = self.images

        if manual_sort:
            _images: PImage = filter(lambda img: img.position == -1, self.images)

        if len(_images) < 1:
            raise ValueError("Must have some images to convert")

        img_output = _images[0].img.convert("RGB")
        img_other = (_img.img.convert("RGB") for _img in _images[1:])
        img_output.save(
            f'{self.path}/{name}.pdf', 'PDF',
            resolution=100.0, save_all=True,
            append_images=img_other
        )

class CLI:
    def __init__(self):
        self.name = 'Default'
        self.comix: PComix = None
        self.context = Context.load_pages
        self.selected_img = 0
        self.with_manual = False
        self.run = True

        while self.run:
            self.render_interface()


        map(lambda f: f.close(), opened_files)
        print('Goodbye!~ Hope I helped you')
        sleep(1.2)


    def unknown(self):
        print('Unknown function number')
        sleep(0.7)

    @staticmethod
    def clear():
        if os.name == 'nt':
            os.system('CLS')
        else:
            os.system('clear')

    def render_interface(self):
        if self.context == Context.load_pages:
            print(
                'ComiXPDF by @rud356\n',
                f'Loaded comix: {self.comix is not None}',
                f'Comix name: {self.name}',
                '1) Load comix folder',
                sep='\n'
                )

            if self.comix is not None:
                print(
                '2) set output name',
                '3) sort by names',
                '4) sort by dates',
                '5) sort by manual position',
                '6) render comix',
                '7) Images manager',
                sep='\n'
                )

            print(
                f'm) Manual sort mode: {self.with_manual}',
                'x) close program',
                sep='\n'
                )

            try:
                selected = input('> ')
                if selected == 'm':
                    self.with_manual = not self.with_manual
                    self.clear()
                    return

                if selected == 'x':
                    self.run = False
                    self.clear()
                    return

                selected = int(selected)
                if selected not in range(1, 8):
                    raise ValueError()

            except ValueError:
                print('Must be an int beetwin 1 and 7 inclusive!')
                sleep(0.7)
                self.clear()
                return

            if self.comix is None and selected in range(3, 8):
                print('Load comix firstly!')
                sleep(0.7)
                self.clear()
                return

            if selected == 7:
                self.context = Context.image_selection
                self.clear()
                return

            if selected == 6:
                print('Rendering pdf in progress...')
                self.comix.create_pdf(self.name)
                print('Finished!')
                sleep(0.7)
                self.clear()
                return

            _ = {
                1: self.load_comix,
                2: self.comix_name,
            }
            if self.comix is not None:
                _.update({
                    3: self.comix.sort_names,
                    4: self.comix.sort_time,
                    5: self.comix.sort_position,
                })
            _.get(selected, self.unknown)()

        elif self.context == Context.image_selection:
            print('x) to main page')
            for n, img_info in enumerate(self.comix.image_list()):
                print(
                    f'{n}) {img_info.filename} | manual position {img_info.position}'
                )

            selected = input('> ')
            if selected == 'x':
                self.context = Context.load_pages
                self.clear()
                return

            try:
                selected = int(selected)
                if not (0 <= selected < len(self.comix.image_list())):
                    raise ValueError()

            except ValueError:
                print(f'Integers in range from 0 to {len(self.comix.image_list)-1}')
                sleep(0.7)
                self.clear()
                return

            self.selected_img = selected
            self.context = Context.image_selected

        elif self.context == Context.image_selected:
            image: PImage = self.comix.image_list()[self.selected_img]
            print(
                ' x) to image selection',
                ' 1) show image',
                ' 2) set position',
                sep='\n'
            )

            selected = input('> ')

            if selected == 'x':
                self.context = Context.image_selection
                self.clear()
                return

            elif selected == '1':
                image.show()
                self.clear()
                return

            elif selected == '2':
                temp_images = list(filter(lambda img: img.position != -1, self.comix.image_list))
                temp_images.sort(key=PImage.position)

                try:
                    new_position = int(input('new position> '))
                    if new_position > -1:
                        image.position = new_position

                        for img in temp_images:
                            img.position += 1

                    elif new_position == -1:
                        image.position = new_position

                    else:
                        raise ValueError()

                except ValueError:
                    print('Position should be >= -1')
                    sleep(0.7)
                    self.clear()

            else:
                self.unknown()

        else:
            self.unknown()


    def load_comix(self):
        self.name = "Default"
        try:
            load_path = input('comix path> ')
            self.comix = PComix(load_path)

        except ValueError as e:
            print(e)
            sleep(0.7)

        finally:
            self.clear()

    def comix_name(self):
        self.name = input('comix name> ')

    @classmethod
    def start(cls):
        return cls()

if __name__ == "__main__":
    CLI()