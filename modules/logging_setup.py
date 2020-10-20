import logging

from config import config


handlers = [logging.FileHandler(filename=config.log_path, encoding='utf-8', mode='a+')]
logging.basicConfig(level=getattr(logging, config.log_level), handlers=handlers)
