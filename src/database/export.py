import config as cnfg

import utils.formatter as ff
import utils.inputter as ii
import utils.menu as mm
import utils.other as oo
import utils.validator as vv

import database.tools.executor as exe

from pathlib import Path
from tkinter import filedialog
import tkinter as tk
import re


# DB_NAME = cnfg.config['db_connection']['database']

TIMINGS_ALIAS = cnfg.config['table_references']['timings']
TIMINGS_HISTORY_ALIAS = cnfg.config['table_references']['timings_history']

GUI = cnfg.config['operations']['import_export']['file_selection_options']['GUI']
DEFAULT = cnfg.config['operations']['import_export']['file_selection_options']['Default']
PATH = cnfg.config['operations']['import_export']['file_selection_options']['Path']

FILE_SELECTION_OPTIONS = (GUI, DEFAULT, PATH)

TABLE_CONFIG = {
    TIMINGS_ALIAS: {
        'table_name': "timings",
        'export_sql': "\\copy timings TO '{file_path}' WITH (FORMAT csv);",
        'default_location': cnfg.config['default_export_locations']['timings'],
        'default_filename': cnfg.config['default_export_filenames']['timings']
    },
    TIMINGS_HISTORY_ALIAS: {
        'table_name': "timings_history",
        'export_sql': "\\copy timings_history TO '{file_path}' WITH (FORMAT csv);",
        'default_location': cnfg.config['default_export_locations']['timings_history'],
        'default_filename': cnfg.config['default_export_filenames']['timings_history']
    }
}

EVERYTHING_ALIAS = cnfg.config['everything_reference']


def export_manager(table, method=None) -> None:
    if table == EVERYTHING_ALIAS:
        if not method:
            LIMITED_METHOD_OPTIONS = (GUI, DEFAULT)
            mm.display_menu(title="FILE SELECTION?", options=tuple(opt.capitalize() for opt in LIMITED_METHOD_OPTIONS))
            method = ii.get_user_input()

            if not method:
                return
        
        if method == GUI:
            print()
            _gui_exec(table=TIMINGS_ALIAS)
            _gui_exec(table=TIMINGS_HISTORY_ALIAS)
            return
        elif method == DEFAULT:
            print()
            _default_exec(table=TIMINGS_ALIAS)
            _default_exec(table=TIMINGS_HISTORY_ALIAS)
            return
        else:
            ff.print_colored(text=f"INVALID CHOICE '{method}'. ONLY '{GUI}' AND '{DEFAULT}' ALLOWED.\n", color="YELLOW")
            return

    if table not in (TIMINGS_ALIAS, TIMINGS_HISTORY_ALIAS):
        ff.print_colored(text=f"INVALID TABLE '{table}'.\n", color="YELLOW")
        return
    
    all_ok, info_message = oo.get_db_exists_state(table=_get_table_name(table=table))
    if not all_ok:
        ff.print_colored(text=f"{_get_unsuccessful_export_message(table=table)} {info_message}\n", color="YELLOW")
        return
    
    if method:
        if method == GUI:
            _gui_exec(table=table)
        elif method == DEFAULT:
            _default_exec(table=table)
        else:
            _path_exec(table=table, file_path=method)
        return

    mm.display_menu(title="FILE SELECTION?", options=tuple(opt.capitalize() for opt in FILE_SELECTION_OPTIONS))
    method_choice = ii.get_user_input()
    
    if not vv.validate_choice(choice=method_choice, valid_options=FILE_SELECTION_OPTIONS):
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
    
    directory_path = filedialog.askdirectory(
        title=f"Select directory to save the file from a table: {_get_table_name(table=table)}"
    )
    
    root.destroy()
    
    if not directory_path:
        return
    
    DEFAULT_FILENAME = TABLE_CONFIG[table]['default_filename']
    
    if not _validate_csv_filename(filename=DEFAULT_FILENAME):
        ff.print_colored(text=f"{_get_unsuccessful_export_message(table=table)} INVALID DEFAULT FILENAME in config.json FOR TABLE '{_get_table_name(table=table)}'.\n", color="YELLOW")
        return
    
    FilePath = Path(directory_path) / DEFAULT_FILENAME

    _call_export(table=table, file_path=FilePath)

def _default_exec(table) -> None:
    is_valid, DirPath = _validate_directory_path(path=TABLE_CONFIG[table]['default_location'].format(database=_get_database_name()), table=table, simple_validation=False)
    
    if not is_valid:
        ff.print_colored(text=f"{_get_unsuccessful_export_message(table=table)} INVALID DEFAULT DIRECTORY PATH in config.json FOR TABLE '{_get_table_name(table=table)}'.\n", color="YELLOW")
        return
    
    is_valid, FileName = _validate_csv_filename(filename=TABLE_CONFIG[table]['default_filename'])
    
    if not is_valid:
        ff.print_colored(text=f"{_get_unsuccessful_export_message(table=table)} INVALID DEFAULT FILENAME in config.json FOR TABLE '{_get_table_name(table=table)}'.\n", color="YELLOW")
        return
    
    FilePath = DirPath / FileName
    
    _call_export(table=table, file_path=FilePath)

def _path_exec(table, file_path) -> None:
    is_valid, FilePath = _validate_file_path(path=file_path, table=table)

    if not is_valid:
        ff.print_colored(text=f"{_get_unsuccessful_export_message(table=table)} INVALID FILE PATH.\n", color="YELLOW")
        return

    _call_export(table=table, file_path=FilePath)


def _validate_file_path(path, table) -> tuple[bool, Path | None]:
    if not path.strip():
        return False, None

    path = path.replace('"', '').replace("'", '')

    FilePath = Path(path)
    directory = FilePath.parent
    filename = FilePath.name

    is_dir_valid, DirPath = _validate_directory_path(path=str(directory), table=table)
    if not is_dir_valid:
        return False, None
    
    is_filename_valid, FileName = _validate_csv_filename(filename=filename)
    if not is_filename_valid:
        return False, None
    
    FilePath = DirPath / FileName
    return True, FilePath

def _validate_directory_path(path, table, simple_validation=True) -> tuple[bool, Path | None]: 
    if not path.strip():
        return False, None
    
    path = path.replace('"', '').replace("'", '')
    
    DirPath = Path(path)
    DirPath = DirPath.resolve()

    # PATH from config.json with {}
    if not simple_validation:
        # Parent doesn't exist -> instant return
        if not DirPath.parent.exists() or not DirPath.parent.is_dir():
            return False, DirPath
        
        try:
            DirPath.mkdir(exist_ok=True)
        except Exception:
            ff.print_colored(text=f"FAILED TO CREATE EXPORT DIRECTORY FOR DATABASE '{_get_database_name()}' TABLE '{_get_table_name(table=table)}'", color="RED")
            return False, DirPath

    if not DirPath.exists() or not DirPath.is_dir():
        return False, DirPath

    return True, DirPath

def _validate_csv_filename(filename) -> tuple[bool, str | None]:
    # At least one character as file name + .csv
    pattern = r'^.+\.csv$'
    filename = filename.strip()
    
    if re.match(pattern, filename, re.IGNORECASE):
        name_part = filename[:-4].strip()
        return len(name_part) > 0, filename
    return False, None


def _call_export(table, file_path) -> None:
    result = exe.execute_query(sql=TABLE_CONFIG[table]['export_sql'].format(file_path=file_path), header=False, capture=True)

    ff.print_colored(text=f"EXPORT FROM '{_get_table_name(table=table)}' SUCCESSFUL. {result.stdout.split()[1]} ROWS.\n", color="GREEN")


def _get_unsuccessful_export_message(table) -> str:
    return f"EXPORT FROM '{_get_table_name(table=table)}' UNSUCCESSFUL."

def _get_table_name(table) -> str:
    return TABLE_CONFIG[table]['table_name']

def _get_database_name() -> str:
    return cnfg.config['db_connection']['database']
