import utils.formatter as ff

import sys
import subprocess
from typing import NoReturn


def restart_exec() -> NoReturn:
    ff.print_colored(text="RESTARTING PROGRAM...\n", color="GREEN")
    subprocess.run(args=["python", "-u", "main.py"], check=True)
    sys.exit(0)
