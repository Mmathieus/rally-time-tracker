import config as cnfg

import utils.formatter as ff
import utils.inputter as ii
import utils.validator as vv

import database.tools.state as stt

import services.dashboard as dshbrd


ALL_DATABASES = cnfg.config['database']['available_databases']


def switch_manager(database=None) -> None:
    # Default db must be in all_db list in config
    if not _check_current_db_in_config_list():
        return

    # Select distinct database names from all_db list
    VALID_DATABASES = _get_valid_databases()

    # 'database' not typed
    if not database:
        # Only 1 in list -> switch on it
        if len(VALID_DATABASES) == 1:
            database, = VALID_DATABASES
        # More than 1 to choose from
        else:
            ff.display_menu(title="DATABASE OPTIONS", options=VALID_DATABASES)
            database = ii.get_user_input(autocomplete_options=VALID_DATABASES)
            if not database:
                print()
                return

    CURRENT_DB = cnfg.DB_NAME

    # Switch to current db -> no need for that
    if database == CURRENT_DB:
        ff.print_colored(text=f"ALREADY ON '{CURRENT_DB}' DATABASE.\n", color="YELLOW")
        return

    # Validate 'database' typed by user
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


def _check_current_db_in_config_list() -> bool:
    CURRENT_DB = cnfg.DB_NAME.lower()

    if CURRENT_DB not in ALL_DATABASES:
        ff.print_colored(text=f"CURRENT DATABASE '{CURRENT_DB}' MISSING IN 'available_databases' LIST IN config.json.\n", color="YELLOW")
        return False
    return True

def _get_valid_databases() -> list:
    seen = set()
    valid_databases = []

    # Iterate through all databases and remove duplicates
    for db in ALL_DATABASES:
        # Normalize for comparison (case-insensitive, trimmed)
        db_normalized = db.strip().lower()

        # Skip current database or duplicates
        if db_normalized == cnfg.DB_NAME or db_normalized in seen:
            continue
        
        # Add original value to results and mark as seen
        valid_databases.append(db)
        seen.add(db_normalized)
    
    return valid_databases
