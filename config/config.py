import pathlib
import atexit
from functools import partial
from configparser import ConfigParser

from betterconf import field, Config, caster
from betterconf.config import AbstractProvider, Field
from custom_types.image_sorters import ImageSorterKeys

config_file_path = pathlib.Path(__file__).parent / "config.cfg"


class ConfigparserProvider(AbstractProvider):
    def __init__(self, config_path):
        self.config = ConfigParser()
        self.config.read(config_path)

    def get(self, name: str):
        return self.config.get('ComixPDF', name)


field = partial(field, provider=ConfigparserProvider(config_file_path))


class ResolutionCaster(caster.AbstractCaster):
    def cast(self, val):
        try:
            return [int(i) for i in val.split('x', 1)][:2]

        except ValueError:
            return [512, 512]


class ImageSorterCaster(caster.AbstractCaster):
    def cast(self, sorter: str):
        getattr(ImageSorterKeys, sorter, ImageSorterKeys.modification_timestamp_key)


class ComixPDFConfig(Config):
    # TODO: add resolution of output and quality params
    # Image loading
    cache_thumbnails: bool = field('cache_thumbnails', caster=caster.to_bool)
    thumbnails_size: list = field('thumbnails_size', caster=ResolutionCaster)
    border_size: int = field(caster=caster.to_int)

    # Comix loading
    _default_sort_mode: callable = field(caster=ImageSorterCaster)
    reversed_sorting: bool = field(caster=caster.to_bool, default=False)

    # Comix optimizations
    optimized: bool = field(caster=caster.to_bool, default=True)

    # Logs
    log_path: str = field(default='~./comix_pdf.log')
    log_level: str = field(default='ERROR')

    @property
    def default_sort_mode(self):
        return self._default_sort_mode

    @default_sort_mode.setter
    def default_sort_mode(self, value):
        try:
            self.default_sort_mode = getattr(ImageSorterKeys, value)

        except AttributeError:
            raise ValueError("Invalid sorting method name")

    def dump_config(self):
        config_temp = ConfigParser()
        config_temp.add_section('ComixPDF')

        set_var = partial(config_temp.set, section='ComixPDF')

        # By using dir(self) we will get all names of vars inside
        for name in dir(ComixPDFConfig):
            # There we checking if type of attr is Field (from betterconf)
            if isinstance(getattr(ComixPDFConfig, name), Field):
                # Here we set this var to our config
                # If we got the function (ImageSorter key) - we do save its name
                if callable(getattr(self, name)):
                    set_var(getattr(self, name).__name__)

                set_var(name, getattr(self, name))

        config_temp.write(config_file_path)


config = ComixPDFConfig()
atexit.register(config.dump_config())

__all__ = ["config"]
