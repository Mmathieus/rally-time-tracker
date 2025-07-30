import utils.formatter as ff

from typing import NoReturn
import sys
import subprocess


def restart_program() -> NoReturn:
    ff.print_colored(text="RESTARTING PROGRAM...\n", color="GREEN")
    subprocess.run(args=["python", "-u", "main.py"], check=True)
    sys.exit(0)
