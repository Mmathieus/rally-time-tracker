import config as cnfg

import utils.formatter as ff
import utils.inputter as ii
import utils.validator as vv

import database.tools.executor as exe
import database.tools.sequence as sqnc
import database.tools.other as othr

from pathlib import Path
from tkinter import filedialog
import tkinter as tk
import re
import os


GUI = cnfg.config['command']['import__export']['location_selection']['GUI']
DEFAULT = cnfg.config['command']['import__export']['location_selection']['Default']
PATH = cnfg.config['command']['import__export']['location_selection']['Path']

METHOD_OPTIONS = (GUI, DEFAULT, PATH)

TABLE_CONFIG = {
    cnfg.PRIMARY_TB_ALIAS: {
        'import_sql': "\\copy timings FROM '{file_path}' WITH (FORMAT csv);",
        'default_location': cnfg.config['command']['import']['default_file_path']['primary_table']
    },
    cnfg.HISTORY_TB_ALIAS: {
        'import_sql': "\\copy timings_history FROM '{file_path}' WITH (FORMAT csv);",
        'default_location': cnfg.config['command']['import']['default_file_path']['history_table']
    }
}


def import_manager(table, method=None, override=None) -> None:
    # Import on both tables
    if table == cnfg.EVERYTHING_ALIAS:
        # Selecting file-selection method (Path method excluded (file path is part of the command call and can't be typed afterwards))
        if not method:
            LIMITED_METHOD_OPTIONS = (GUI, DEFAULT)
            ff.display_menu(title="FILE SELECTION", options=tuple(opt.capitalize() for opt in LIMITED_METHOD_OPTIONS))
            method = ii.get_user_input()

            if not method:
                print()
                return

        if method == GUI:
            _gui_exec(table=cnfg.PRIMARY_TB_ALIAS, override=override)
            _gui_exec(table=cnfg.HISTORY_TB_ALIAS, override=override)
            return
        elif method == DEFAULT:
            _default_exec(table=cnfg.PRIMARY_TB_ALIAS, override=override)
            _default_exec(table=cnfg.HISTORY_TB_ALIAS, override=override)
            return
        else:
            print(
                f"{ff.colorize(text=f"INVALID CHOICE '{method}'.", color="RED")} "
                f"{ff.colorize(text=f" ONLY '{GUI}' AND '{DEFAULT}' ALLOWED.", color="YELLOW")}\n"
            )
            return

    # Check table name
    if table not in cnfg.BOTH_TABLES:
        ff.print_colored(text=f"INVALID TABLE '{table}'.\n", color="RED")
        return
    
    # Check if DB/TABLE exists
    all_ok, info_message = othr.get_db_exists_state(table=cnfg.get_tb_name(table=table))
    if not all_ok:
        ff.print_colored(text=f"{_get_unsuccessful_import_message(table=table)} {info_message}\n", color="YELLOW")
        return
    
    # Method was selected
    if method:
        if method == GUI:
            _gui_exec(table=table, override=override)
        elif method == DEFAULT:
            _default_exec(table=table, override=override)
        else:
            _path_exec(table=table, file_path=method, override=override)
        return

    # Method wasn't selected - Asking for it
    ff.display_menu(title="FILE SELECTION", options=tuple(opt.capitalize() for opt in METHOD_OPTIONS))
    method_choice = ii.get_user_input()
    
    # Validating selected method
    validated, validation_message = vv.validate_choice(choice=method_choice, valid_options=METHOD_OPTIONS)
    if not validated:
        if validation_message:
            print(ff.colorize(text=validation_message, color="RED"))
        print()
        return
    
    # Calling import (asking for path if selected method is Path)
    if method_choice == GUI:
        _gui_exec(table=table, override=override)
    elif method_choice == DEFAULT:
        _default_exec(table=table, override=override)
    else:
        file_path = ii.get_user_input(prompt="Enter full path to the CSV file including the file name and .csv", lowercase=False)
        _path_exec(table=table, file_path=file_path, override=override)


def _gui_exec(table, override) -> None:
    root = tk.Tk()
    root.withdraw()
    
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

def _path_exec(table, file_path, override) -> None:
    # Checking file path from user
    is_valid, FilePath = _validate_file_path(path=file_path)

    if not is_valid:
        ff.print_colored(text=f"{_get_unsuccessful_import_message(table=table)} INVALID FILE PATH.\n", color="YELLOW")
        return

    _call_import(table=table, file_path=FilePath, override=override)


def _validate_file_path(path) -> tuple[bool, Path | None]: 
    # If empty
    if not path.strip():
        return False, None
    
    # Quotation marks removed
    path = path.replace('"', '').replace("'", '')
    
    FilePath = Path(path)
    FilePath = FilePath.resolve()
    
    if not FilePath.exists() or not FilePath.is_file() or FilePath.suffix.lower() != '.csv':
        return False, FilePath
    return True, FilePath

def _call_import(table, file_path, override) -> None:
    doing_override = _should_override(override=override)
    # result = None
    # override_message = ""

    if doing_override:
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


def _should_override(override) -> bool:
    if override:
        OVERRIDE_OPTIONS = cnfg.config['command']['import']['override_data_options']

        validated, validation_message = vv.validate_choice(choice=override, valid_options=OVERRIDE_OPTIONS)
        # No need to print that 'override' choice is OK. If it's not, validated=False automatically
        return validated

    # If override not selected. Using value from config.json
    return cnfg.config['command']['import']['override_data_on_import']


def _get_unsuccessful_import_message(table) -> str:
    return f"IMPORT INTO '{cnfg.get_tb_name(table=table)}' UNSUCCESSFUL."
