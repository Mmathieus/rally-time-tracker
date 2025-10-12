import config as cnfg

import utils.formatter as ff
import utils.inputter as ii
import utils.menu as mm
import utils.validator as vv

import database.tools.executor as exe
import database.tools.other as othr

from pathlib import Path
from tkinter import filedialog
import tkinter as tk
import re


GUI = cnfg.config['command']['import__export']['location_selection']['GUI']
DEFAULT = cnfg.config['command']['import__export']['location_selection']['Default']
PATH = cnfg.config['command']['import__export']['location_selection']['Path']

METHOD_OPTIONS = (GUI, DEFAULT, PATH)

TABLE_CONFIG = {
    cnfg.PRIMARY_TB_ALIAS: {
        'export_sql': "\\copy timings TO '{file_path}' WITH (FORMAT csv);",
        'default_location': cnfg.config['command']['export']['default_folder_path']['primary_table'],
        'default_file_name': cnfg.config['command']['export']['default_file_name']['primary_table']
    },
    cnfg.HISTORY_TB_ALIAS: {
        'export_sql': "\\copy timings_history TO '{file_path}' WITH (FORMAT csv);",
        'default_location': cnfg.config['command']['export']['default_folder_path']['history_table'],
        'default_file_name': cnfg.config['command']['export']['default_file_name']['history_table']
    }
}


def export_manager(table, method=None) -> None:
    # Export on both tables
    if table == cnfg.EVERYTHING_ALIAS:
        # Selecting folder-selection method (Path method excluded (file path is part of the command call and can't be typed afterwards))
        if not method:
            LIMITED_METHOD_OPTIONS = (GUI, DEFAULT)
            mm.display_menu(title="FILE SELECTION", options=tuple(opt.capitalize() for opt in LIMITED_METHOD_OPTIONS))
            method = ii.get_user_input()

            if not method:
                print()
                return
        
        if method == GUI:
            print()
            _gui_exec(table=cnfg.PRIMARY_TB_ALIAS)
            _gui_exec(table=cnfg.HISTORY_TB_ALIAS)
            return
        elif method == DEFAULT:
            print()
            _default_exec(table=cnfg.PRIMARY_TB_ALIAS)
            _default_exec(table=cnfg.HISTORY_TB_ALIAS)
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
        ff.print_colored(text=f"{_get_unsuccessful_export_message(table=table)} {info_message}\n", color="YELLOW")
        return
    
    # Method was selected
    if method:
        if method == GUI:
            _gui_exec(table=table)
        elif method == DEFAULT:
            _default_exec(table=table)
        else:
            _path_exec(table=table, file_path=method)
        return

    # Method wasn't selected - Asking for it
    mm.display_menu(title="FILE SELECTION", options=tuple(opt.capitalize() for opt in METHOD_OPTIONS))
    method_choice = ii.get_user_input()
    
    # Validating selected method
    validated, validation_message = vv.validate_choice(choice=method_choice, valid_options=METHOD_OPTIONS)
    if not validated:
        if validation_message:
            print(ff.colorize(text=validation_message, color="RED"))
        print()
        return
    
    # Calling export (asking for path if selected method is Path)
    if method_choice == GUI:
        _gui_exec(table=table)
    elif method_choice == DEFAULT:
        _default_exec(table=table)
    else:
        file_path = ii.get_user_input(prompt="Enter full path to the CSV file including the file name and .csv", lowercase=False)
        _path_exec(table=table, file_path=file_path)


def _gui_exec(table) -> None:
    root = tk.Tk()
    root.withdraw()
    
    directory_path = filedialog.askdirectory(
        title=f"Select directory to save the file from table: {cnfg.get_tb_name(table=table)}"
    )
    
    root.destroy()
    
    # Cancelled folder path selection
    if not directory_path:
        print()
        return
    
    DEFAULT_FILE_NAME = TABLE_CONFIG[table]['default_file_name']
    # Validating file name (*.csv) from config.json
    is_valid, FileName = _validate_csv_filename(filename=DEFAULT_FILE_NAME)
    if not is_valid:
        ff.print_colored(text=f"{_get_unsuccessful_export_message(table=table)} INVALID DEFAULT FILENAME in config.json FOR TABLE '{cnfg.get_tb_name(table=table)}'.\n", color="YELLOW")
        return
    
    FilePath = Path(directory_path) / DEFAULT_FILE_NAME

    _call_export(table=table, file_path=FilePath)

def _default_exec(table) -> None:
    # Validating folder. {database} must be included in folder path, in config.json
    is_valid, DirPath = _validate_directory_path(path=TABLE_CONFIG[table]['default_location'].format(database=cnfg.DB_NAME), table=table, simple_validation=False)
    
    if not is_valid:
        ff.print_colored(text=f"{_get_unsuccessful_export_message(table=table)} INVALID DEFAULT DIRECTORY PATH in config.json FOR TABLE '{cnfg.get_tb_name(table=table)}'.\n", color="YELLOW")
        return
    
    # Validating file name
    is_valid, FileName = _validate_csv_filename(filename=TABLE_CONFIG[table]['default_file_name'])
    
    if not is_valid:
        ff.print_colored(text=f"{_get_unsuccessful_export_message(table=table)} INVALID DEFAULT FILENAME in config.json FOR TABLE '{cnfg.get_tb_name(table=table)}'.\n", color="YELLOW")
        return
    
    FilePath = DirPath / FileName
    
    _call_export(table=table, file_path=FilePath)

def _path_exec(table, file_path) -> None:
    # Checking file path from user
    is_valid, FilePath = _validate_file_path(path=file_path, table=table)

    if not is_valid:
        ff.print_colored(text=f"{_get_unsuccessful_export_message(table=table)} INVALID FILE PATH.\n", color="YELLOW")
        return

    _call_export(table=table, file_path=FilePath)


def _validate_file_path(path, table) -> tuple[bool, Path | None]:
    # If empty
    if not path.strip():
        return False, None

    # Quotation marks removed
    path = path.replace('"', '').replace("'", '')

    # Split whole file path to: Directory & File_Name
    FilePath = Path(path)
    directory = FilePath.parent
    filename = FilePath.name

    # Checking folder
    is_dir_valid, DirPath = _validate_directory_path(path=str(directory), table=table)
    if not is_dir_valid:
        return False, None
    
    # Checking file name
    is_filename_valid, FileName = _validate_csv_filename(filename=filename)
    if not is_filename_valid:
        return False, None
    
    FilePath = DirPath / FileName
    return True, FilePath

def _validate_directory_path(path, table, simple_validation=True) -> tuple[bool, Path | None]: 
    # If empty
    if not path.strip():
        return False, None
    
    # Quotation marks removed
    path = path.replace('"', '').replace("'", '')
    
    DirPath = Path(path)
    DirPath = DirPath.resolve()

    # PATH from config.json with {}
    if not simple_validation:
        # Parent doesn't exist -> instant return
        if not DirPath.parent.exists() or not DirPath.parent.is_dir():
            return False, None
        
        try:
            DirPath.mkdir(exist_ok=True)
        except Exception:
            ff.print_colored(text=f"FAILED TO CREATE EXPORT DIRECTORY FOR DATABASE '{cnfg.DB_NAME}' TABLE '{cnfg.get_tb_name(table=table)}'", color="RED")
            return False, None

    if not DirPath.exists() or not DirPath.is_dir():
        return False, None

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

    ff.print_colored(text=f"EXPORT FROM '{cnfg.get_tb_name(table=table)}' SUCCESSFUL. {result.stdout.split()[1]} ROWS.\n", color="GREEN")


def _get_unsuccessful_export_message(table) -> str:
    return f"EXPORT FROM '{cnfg.get_tb_name(table=table)}' UNSUCCESSFUL."
