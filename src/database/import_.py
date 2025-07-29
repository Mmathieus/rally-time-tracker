import config as cnfg

import utils.inputter as ii
import utils.formatter as ff
import utils.validator as vv
import utils.menu as mm
import utils.other as oo

import database.tools.executor as exe
import database.tools.sequence as sqnc

from pathlib import Path
from tkinter import filedialog
import tkinter as tk
import re


TIMINGS_ALIAS = cnfg.config['table_references']['timings']
TIMINGS_HISTORY_ALIAS = cnfg.config['table_references']['timings_history']

GUI = cnfg.config['operations']['import_export']['file_selection_options']['GUI']
DEFAULT = cnfg.config['operations']['import_export']['file_selection_options']['Default']
PATH = cnfg.config['operations']['import_export']['file_selection_options']['Path']

METHOD_OPTIONS = (GUI, DEFAULT, PATH)

TABLE_CONFIG = {
    TIMINGS_ALIAS: {
        'table_name': "timings",
        'import_sql': "\\copy timings FROM '{file_path}' WITH (FORMAT csv);",
        'default_location': cnfg.config['default_import_locations']['timings']
    },
    TIMINGS_HISTORY_ALIAS: {
        'table_name': "timings_history",
        'import_sql': "\\copy timings_history FROM '{file_path}' WITH (FORMAT csv);",
        'default_location': cnfg.config['default_import_locations']['timings_history']
    }
}


def import_manager(table, method=None) -> None:
    if table not in (TIMINGS_ALIAS, TIMINGS_HISTORY_ALIAS):
        ff.print_colored(text=f"INVALID TABLE '{table}'.\n", color="YELLOW")
        return
    
    all_ok, info_message = oo.get_db_exists_state(table=_get_table_name(table=table))
    if not all_ok:
        ff.print_colored(text=f"{_get_unsuccessful_import_message(table=table)} {info_message}\n", color="YELLOW")
        return
    
    if method:
        if method == GUI:
            _gui_exec(table=table)
        elif method == DEFAULT:
            _default_exec(table=table)
        else:
            _path_exec(table=table, file_path=method)
        return

    mm.display_menu(title="FILE SELECTION?", options=tuple(opt.capitalize() for opt in METHOD_OPTIONS))
    method_choice = ii.get_user_input()
    
    if not vv.validate_choice(choice=method_choice, valid_options=METHOD_OPTIONS):
        return
    
    if method_choice == GUI:
        _gui_exec(table=table)
    elif method_choice == DEFAULT:
        _default_exec(table=table)
    else:
        file_path = ii.get_user_input(prompt="Enter the full path to the CSV file including the file name and .csv", lowercase=False)
        _path_exec(table=table, file_path=file_path)


def _gui_exec(table) -> None:
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.askopenfilename(
        title="Select a CSV file",
        filetypes=[("CSV files", "*.csv")]
    )
    
    root.destroy()
    
    if not file_path:
        return
    
    FilePath = Path(file_path)

    _call_import(table=table, file_path=FilePath)

def _default_exec(table) -> None:
    is_valid, FilePath = _validate_file_path(path=TABLE_CONFIG[table]['default_location'])
    
    if not is_valid:
        ff.print_colored(text=f"{_get_unsuccessful_import_message(table=table)} INVALID DEFAULT FILE PATH in config.json FOR TABLE '{_get_table_name(table=table)}'.\n", color="YELLOW")
        return
    
    _call_import(table=table, file_path=FilePath)

def _path_exec(table, file_path) -> None:
    is_valid, FilePath = _validate_file_path(path=file_path)

    if not is_valid:
        ff.print_colored(text=f"{_get_unsuccessful_import_message(table=table)} INVALID FILE PATH.\n", color="YELLOW")
        return

    _call_import(table=table, file_path=FilePath)


def _validate_file_path(path) -> tuple[bool, Path | None]: 
    if not path.strip():
        return False, None
    
    path = path.replace('"', '').replace("'", '')
    
    FilePath = Path(path)
    FilePath = FilePath.resolve()
    
    if not FilePath.exists() or not FilePath.is_file() or FilePath.suffix.lower() != '.csv':
        return False, FilePath
    return True, FilePath

def _call_import(table, file_path) -> None:    
    result = exe.execute_query(sql=TABLE_CONFIG[table]['import_sql'].format(file_path=file_path), header=False, capture=True, check=False)

    if result.stderr and "duplicate key value" in result.stderr.strip():
        ff.print_colored(text=f"{_get_unsuccessful_import_message(table=table)} DUPLICATE ID '{re.search(r'\((\d+)\)', result.stderr).group(1)}' FOUND.\n", color="YELLOW")
        return

    ff.print_colored(text=f"IMPORT INTO '{_get_table_name(table=table)}' SUCCESSFUL. {result.stdout.split()[1]} ROWS.\n", color="GREEN")

    # sqnc.update_sequence(calling_from=_get_table_name(table=table))


def _get_unsuccessful_import_message(table) -> str:
    return f"IMPORT INTO '{_get_table_name(table=table)}' UNSUCCESSFUL."

def _get_table_name(table) -> str:
    return TABLE_CONFIG[table]['table_name']
