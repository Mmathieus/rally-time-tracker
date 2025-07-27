import utils.formatter as ff

import sys
from typing import NoReturn


def end_exec() -> NoReturn:
    ff.print_colored(text="Have a great rest of your day Sir", color="CYAN")
    sys.exit(0)
