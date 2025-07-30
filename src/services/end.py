import utils.formatter as ff

from typing import NoReturn
import sys


def end_program() -> NoReturn:
    ff.print_colored(text="Have a great rest of your day Sir", color="CYAN")
    sys.exit(0)
