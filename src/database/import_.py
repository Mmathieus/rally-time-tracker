import config as cnfg

import utils.formatter as ff
import utils.inputter as ii
import utils.validator as vv
import utils.other as u_othr

import database.tools.executor as exe
import database.tools.sequence as sqnc
import database.tools.state as stt
import database.tools.other as othr

from pathlib import Path
from tkinter import filedialog
import tkinter as tk
import re
import os


GUI = cnfg.config['command']['import__export']['location_selection']['GUI'].strip()
DEFAULT = cnfg.config['command']['import__export']['location_selection']['Default'].strip()

METHOD_OPTIONS = (GUI, DEFAULT)

OVERRIDE_OPTIONS = cnfg.config['command']['import']['existing_data_options']['override']
DONT_OVERRIDE_OPTIONS = cnfg.config['command']['import']['existing_data_options']['dont_override']
EXISTING_DATA_OPTIONS = OVERRIDE_OPTIONS + DONT_OVERRIDE_OPTIONS

TABLE_CONFIG = {
    cnfg.PRIMARY_TB_ALIAS: {
        'import_sql': "\\copy timings FROM '{file_path}' WITH (FORMAT csv);",
        'default_location': cnfg.config['command']['import']['default_file_path']['primary_table'].strip()
    },
    cnfg.HISTORY_TB_ALIAS: {
        'import_sql': "\\copy timings_history FROM '{file_path}' WITH (FORMAT csv);",
        'default_location': cnfg.config['command']['import']['default_file_path']['history_table'].strip()
    }
}


def import_manager(table, method=None, override=None) -> None:
    # Import on both tables
    if table == cnfg.EVERYTHING_ALIAS:
        
        # Check if DB/TABLES exist
        if not stt.verify_db_exists_state(bad_info_message=ff.colorize(text="IMPORT NOT POSSIBLE. {rest}\n", color="YELLOW")):
            return

        # Determine 'method' value
        method = _determine_method(method=method)
        if not method:
            return
            
        # Determine 'override' value
        override = _determine_override(override=override)
        if not override:
            return
        
        print()
        # GUI 
        if method == GUI:
            import_manager(table=cnfg.PRIMARY_TB_ALIAS, method=GUI, override=override)
            import_manager(table=cnfg.HISTORY_TB_ALIAS, method=GUI, override=override)
        # DEFAULT
        else:
            import_manager(table=cnfg.PRIMARY_TB_ALIAS, method=DEFAULT, override=override)
            import_manager(table=cnfg.HISTORY_TB_ALIAS, method=DEFAULT, override=override)
        return
            


    # Check table name
    if table not in cnfg.BOTH_TABLES:
        ff.print_colored(text=f"INVALID TABLE '{table}'.\n", color="RED")
        return
    
    # Check if DB/TABLE exists
    if not stt.check_db_exists_state(
        table=cnfg.get_tb_name(table=table),
        info_message=ff.colorize(text="IMPORT NOT POSSIBLE. {rest}\n", color="YELLOW")
    )[0]:
        return
    

    # Determine 'method' value
    method = _determine_method(method=method)
    if not method:
        return
    
    # Determine 'override' value
    override = _determine_override(override=override)
    if not override:
        return
    
    
    # GUI 
    if method == GUI:
        _gui_exec(table=table, override=override)
    # DEFAULT
    else:
        _default_exec(table=table, override=override)


def _gui_exec(table, override) -> None:
    root = tk.Tk()
    root.withdraw()
    
    # GUI selector
    file_path = filedialog.askopenfilename(
        title=f"Select CSV file for table: {cnfg.get_tb_name(table=table)}",
        filetypes=[("CSV files", "*.csv")]
    )
    
    root.destroy()
    
    # Cancelled file path selection
    if not file_path:
        print()
        return
    
    FilePath = Path(file_path)

    _call_import(table=table, file_path=FilePath, override=override)

def _default_exec(table, override) -> None:
    # {database} must be included in file path, in config.json
    is_valid, FilePath = _validate_file_path(path=TABLE_CONFIG[table]['default_location'].format(database=cnfg.DB_NAME))
    
    if not is_valid:
        ff.print_colored(text=f"{_get_unsuccessful_import_message(table=table)} INVALID DEFAULT FILE PATH in config.json FOR TABLE '{cnfg.get_tb_name(table=table)}'.\n", color="YELLOW")
        return
    
    _call_import(table=table, file_path=FilePath, override=override)


def _call_import(table, file_path, override) -> None:
    if override in OVERRIDE_OPTIONS:
        TABLE_NAME = cnfg.get_tb_name(table=table)

        transaction = f"""
            BEGIN;
                DELETE FROM {TABLE_NAME};
                \\copy {TABLE_NAME} FROM '{file_path}' WITH (FORMAT csv);
            COMMIT;
        """

        tmp_sql_file = othr.create_tmp_sql_file(sql_content=transaction)

        try:
            result = exe.execute_query(file=tmp_sql_file, header=False, capture=True)
            override_message = "PREVIOUS RECORDS OVERRIDDEN."
        finally:
            if os.path.exists(tmp_sql_file):
                os.remove(tmp_sql_file)
    
    else:
        import_sql = TABLE_CONFIG[table]['import_sql'].format(file_path=file_path)
        result = exe.execute_query(sql=import_sql, header=False, capture=True, check=False)
        override_message = ""
    
    if result.stderr:
        if "duplicate key value" in result.stderr.strip():
            duplicate_id = re.search(r'Key\s+\(\w+\)=\((\d+)\)', result.stderr.strip()).group(1)
            ff.print_colored(text=f"{_get_unsuccessful_import_message(table)} DUPLICATE ID '{duplicate_id}' FOUND.\n", color="YELLOW")
            return
        ff.print_colored(text="ERROR IN IMPORT.\n", color="RED")
        return
    
    sqnc.update_sequence()

    imported_rows_count = re.search(r'COPY\s+(\d+)', (result.stdout.strip())).group(1)
    ff.print_colored( text=f"IMPORT INTO '{cnfg.get_tb_name(table=table)}' SUCCESSFUL. {imported_rows_count} ROWS. {override_message}\n", color="GREEN")


def _validate_file_path(path) -> tuple[bool, Path | None]: 
    # If empty
    if not path.strip():
        return False, None
    
    # Quotation marks removed
    path = path.replace('"', '').replace("'", '')
    
    FilePath = Path(path)
    FilePath = FilePath.resolve()
    
    # Conditions
    if not FilePath.exists() or not FilePath.is_file() or FilePath.suffix.lower() != '.csv':
        return False, FilePath
    return True, FilePath


def _determine_method(method) -> str | None:
    #1 - Asking for 'method' if not already typed
    #2 - Validating 'method'

    # Method not typed - Asking for it
    if not method:
        u_othr.display_menu(title="FILE SELECTION", options=tuple(opt.capitalize() for opt in METHOD_OPTIONS))
        method = ii.get_user_input()

    # Validate method
    validated, validation_message = vv.validate_choice(choice=method, valid_options=METHOD_OPTIONS, choice_name="FILE SELECTION")
    if not validated:
        if validation_message:
            ff.print_colored(text=f"{validation_message}", color="RED")
        print()
        return None
    return method

def _determine_override(override) -> str | None:
    #1 - Validating 'override' if already typed
    #2 - Using config.json default 'override' value

    # Validate 'override' typed by user
    if override:
        validated, validation_message = vv.validate_choice(choice=override, valid_options=EXISTING_DATA_OPTIONS, choice_name="OVERRIDE OPTION")
        if not validated:
            ff.print_colored(text=f"{validation_message}\n", color="RED")
            return None
        return override

    # Taking value from config.json
    CONFIG_OVERRIDE_DATA = cnfg.config['command']['import']['override_data_on_import']
    return OVERRIDE_OPTIONS[0] if CONFIG_OVERRIDE_DATA else DONT_OVERRIDE_OPTIONS[0]


def _get_unsuccessful_import_message(table) -> str:
    return f"IMPORT INTO '{cnfg.get_tb_name(table=table)}' UNSUCCESSFUL."
