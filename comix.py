import pathlib
from typing import List
from image import CMXImage

class PComix:
    def __init__(self, path, images):
        self.path = path
        self._title = 'Untitled'
        self.images: List[CMXImage] = images

    @classmethod
    def load_comix(cls, comix_path: str):
        images_path = pathlib.Path(comix_path)
        images = []
        if not images_path.is_dir():
            raise ValueError("Give proper path")

        for image in images_path.iterdir():
            if not image.is_file():
                continue

            try:
                cmximage = CMXImage(image)
                images.append(cmximage)
                cmximage.position = len(images)

            except Exception as e:
                print(e)
                continue

        return cls(images_path, images)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = str(value)

    def sorted_by_order(self, reverse=False):
        self.images.sort(key=CMXImage.position, reverse=reverse)
        for n, image in enumerate(self.images):
            if image.position != -1:
                image.position = n

    def sorted_by_names(self, reverse=False):
        self.images.sort(key=lambda img: img.name, reverse=reverse)
        for n, image in enumerate(self.images):
            if image.position != -1:
                image.position = n

    def sorted_by_dates(self, reverse=False):
        self.images.sort(key=lambda img: img.modified_date, reverse=reverse)
        for n, image in enumerate(self.images):
            if image.position != -1:
                image.position = n

    def get_filtered_images(self):
        listed = list(filter(lambda image: image.position != -1, self.images))
        unlisted = list(filter(lambda image: image.position == -1, self.images))
        return listed, unlisted

    def get_filtered_thumbnails(self):
        listed, unlisted = self.get_filtered_images()

        listed_thumbnails = [image.QThumbnail for image in listed]
        unlisted_thumbnails = [image.QThumbnail for image in unlisted]

        return listed_thumbnails, unlisted_thumbnails

    def get_images_converted(self):
        listed, _ = self.get_filtered_images()
        listed = [image.ConvertedImage for image in listed]
        return listed

    def render_pdf(self):
        images = self.get_images_converted()
        if len(images) == 0:
            raise ValueError("No images added to render")

        first_image = images.pop(0)
        image_info = first_image.info

        first_image.save(
            f'{self.path}/{self.title}.pdf', 'PDF',
            quality=100, optimized=True,
            resolution=100.0, save_all=True,
            append_images=images,
            **image_info
        )
