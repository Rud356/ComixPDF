from config.config import config

import modules.logging_setup
from interfaces.cli import cli

if __name__ == "__main__":
    cli.run_render()
