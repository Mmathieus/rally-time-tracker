import config as cnfg

import utils.formatter as ff
import utils.inputter as ii
import utils.menu as mm
import utils.validator as vv

import database.tools.state as stt

import services.dashboard as dshbrd


ALL_DATABASES = cnfg.config['database']['available_databases']


def switch_manager(database=None) -> None:
    if not _validate_db_names_in_config():
        return

    CURRENT_DB = cnfg.DB_NAME

    VALID_DATABASES = [item for item in ALL_DATABASES if item != CURRENT_DB]

    if not database:
        if len(VALID_DATABASES) == 1:
            database, = VALID_DATABASES
        else:
            mm.display_menu(title="DATABASE OPTIONS", options=VALID_DATABASES)
            database = ii.get_user_input()

            if not database:
                print()
                return

    if database == CURRENT_DB:
        ff.print_colored(text=f"ALREADY ON '{CURRENT_DB}' DATABASE.\n", color="YELLOW")
        return

    validated, validation_message = vv.validate_choice(choice=database, valid_options=VALID_DATABASES)
    if not validated:
        print(f"{ff.colorize(text=validation_message, color="RED")}\n")
        return
    
    ff.print_colored(text="SWITCHING...", color="GREEN")
    
    cnfg.config['database']['credentials']['database'] = database
    cnfg.update_db_name_globally()

    stt.capture_current_db_state()

    ff.print_colored(text=f"SWITCH TO DATABASE '{database}' SUCCESSFUL.\n", color="GREEN")

    if cnfg.config['command']['switch']['dashboard_after_switch']:
        dshbrd.display_dashboard(refresh_db_state=False)


def _validate_db_names_in_config() -> bool:
    CURRENT_DB = cnfg.DB_NAME

    if CURRENT_DB not in ALL_DATABASES:
        ff.print_colored(text=f"CURRENT DATABASE '{CURRENT_DB}' MISSING IN 'available_databases' LIST IN config.json.\n", color="YELLOW")
        return False
    return True

