import config as cnfg

import utils.formatter as ff
import utils.inputter as ii
import utils.menu as mm
import utils.validator as vv

import database.tools.state as stt


1 # Check if request is in config-list

2 # Check if request is the current database

3 # Switch to new database AND update db_connection['database'] in config

4 # SOLVE how to keep updated config after command: restart

5 # ... ?


ALL_DATABASES = cnfg.config['all_databases']


def switch_manager(database=None) -> None:
    if not _validate_db_names_in_config():
        return

    VALID_DATABASES = [item for item in ALL_DATABASES if item != cnfg.config['db_connection']['database']]

    if not database:
        mm.display_menu(title="DATABASE OPTIONS", options=VALID_DATABASES)
        database = ii.get_user_input()

    if not vv.validate_choice(choice=database, valid_options=VALID_DATABASES):
        return
    
    cnfg.config['db_connection']['database'] = database

    ff.print_colored(text=f"SWITCH TO DATABASE '{database}' SUCCESSFUL.\n", color="GREEN")

    stt.capture_current_db_state()


def _validate_db_names_in_config() -> bool:
    CURRENT_DB = cnfg.config['db_connection']['database']

    if CURRENT_DB not in ALL_DATABASES:
        ff.print_colored(text=f"CURRENT DATABASE '{CURRENT_DB}' MISSING IN 'all_databases' LIST IN config.json.\n", color="YELLOW")
        return False
    return True

