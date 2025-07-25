import config as cnfg

import utils.formatter as ff

import sys
import subprocess
from typing import NoReturn


# PROGRAM RESTART
def restart_exec() -> NoReturn:
    ff.print_colored(text="RESTARTING PROGRAM...\n", color="GREEN")
    subprocess.run(args=["python", "-u", "main.py"], check=True)
    sys.exit(0)

# PROGRAM END
def end_exec():
    ff.print_colored(text="Have a great rest of your day Sir", color="CYAN")
    sys.exit(0)


# GETTING DATABASE/TABLE STATE
def get_db_exists_state(table=None, must_exists=True) -> tuple[bool, str | None]:
    # IF db/table must exists    -> then the problem is that it DOESN'T EXISTS.
    # IF db/table mustn't exists -> then the problem is that it EXISTS.
    exists_text = "DOESN'T EXIST" if must_exists else "ALREADY EXISTS"

    status_message = f"DATABASE {exists_text}."
    
    if not cnfg.db_state['database']['exists']:
        return False, status_message
    
    if table:
        status_message = f"TABLE {exists_text}."
        if not cnfg.db_state[table]['exists']:
            return False, status_message
    
    return True, status_message
