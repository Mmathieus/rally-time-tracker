from config import config
import utils.inputter as ii
import utils.formatter as ff
import utils.menu as mm
import utils.validator as vv
import database.others.executor as exe

from pathlib import Path
import tkinter as tk
from tkinter import filedialog

import re


TIMINGS_ALIAS = config['table_references']['timings']
TIMINGS_HISTORY_ALIAS = config['table_references']['timings_history']

GUI = config['operations']['import_export']['file_selection_options']['GUI']
DEFAULT = config['operations']['import_export']['file_selection_options']['Default']
PATH = config['operations']['import_export']['file_selection_options']['Path']

FILE_SELECTION_OPTIONS = (GUI, DEFAULT, PATH)

TABLE_CONFIG = {
    TIMINGS_ALIAS: {
        'table_name': "timings",
        'export_sql': "\\copy timings TO '{file_path}' WITH (FORMAT csv);",
        'default_location': config['default_export_locations']['timings'],
        'default_filename': config['default_export_filenames']['timings']
    },
    TIMINGS_HISTORY_ALIAS: {
        'table_name': "timings_history",
        'export_sql': "\\copy timings_history TO '{file_path}' WITH (FORMAT csv);",
        'default_location': config['default_export_locations']['timings_history'],
        'default_filename': config['default_export_filenames']['timings_history']
    }
}


def _export_manager(table, file_selection=None) -> None:
    if table not in (TIMINGS_ALIAS, TIMINGS_HISTORY_ALIAS):
        ff.print_colored(text=f"INVALID TABLE '{table}'.\n", color="YELLOW")
        return
    
    if file_selection:
        if file_selection == GUI:
            gui_exec(table=table)
        elif file_selection == DEFAULT:
            default_exec(table=table)
        else:
            path_exec(table=table, file_path=file_selection)
        return

    mm.display_menu(title="FILE SELECTION?", options=tuple(opt.capitalize() for opt in FILE_SELECTION_OPTIONS))
    file_selection_choice = ii.get_user_input()
    
    if not vv.validate_choice(choice=file_selection_choice, valid_options=FILE_SELECTION_OPTIONS, choice_type="FILE SELECTION"):
        return
    
    if file_selection_choice == GUI:
        gui_exec(table=table)
    elif file_selection_choice == DEFAULT:
        default_exec(table=table)
    else:
        file_path = ii.get_user_input(prompt="Enter the full path to the CSV file including the file name", lowercase=False)
        path_exec(table=table, file_path=file_path)


def gui_exec(table) -> None:
    root = tk.Tk()
    root.withdraw()
    
    directory_path = filedialog.askdirectory(
        title="Select directory to save the file"
    )
    
    root.destroy()
    
    if not directory_path:
        return
    
    CONFIG_FILENAME = TABLE_CONFIG[table]['default_filename']
    
    if not validate_csv_filename(filename=CONFIG_FILENAME):
        ff.print_colored(text=f"INVALID DEFAULT FILENAME in config.json FOR TABLE '{TABLE_CONFIG[table]['table_name']}'.\n", color="YELLOW")
        return
    
    FilePath = Path(directory_path) / CONFIG_FILENAME

    call_export(table=table, file_path=FilePath)

def default_exec(table) -> None:
    is_valid, DirPath = validate_directory_path(path=TABLE_CONFIG[table]['default_location'])
    
    if not is_valid:
        ff.print_colored(text=f"INVALID DEFAULT DIRECTORY PATH in config.json FOR TABLE '{TABLE_CONFIG[table]['table_name']}'.\n", color="YELLOW")
        return
    
    is_valid, FileName = validate_csv_filename(filename=TABLE_CONFIG[table]['default_filename'])
    
    if not is_valid:
        ff.print_colored(text=f"INVALID DEFAULT FILENAME in config.json FOR TABLE '{TABLE_CONFIG[table]['table_name']}'.\n", color="YELLOW")
        return
    
    FilePath = DirPath / FileName
    
    call_export(table=table, file_path=FilePath)

def path_exec(table, file_path) -> None:
    is_valid, FilePath = validate_file_path(path=file_path)

    if not is_valid:
        ff.print_colored(text=f"INVALID FILE PATH.\n", color="YELLOW")
        return

    call_export(table=table, file_path=FilePath)


def validate_directory_path(path) -> tuple[bool, Path | None]: 
    if not path.strip():
        return False, None
    
    path = path.replace('"', '').replace("'", '')
    
    DirPath = Path(path)
    DirPath = DirPath.resolve()
    
    if not DirPath.exists() or not DirPath.is_dir():
        return False, DirPath
    return True, DirPath

def validate_csv_filename(filename) -> tuple[bool, str | None]:
    # At least one character as file name + .csv
    pattern = r'^.+\.csv$'
    filename = filename.strip()
    
    if re.match(pattern, filename, re.IGNORECASE):
        name_part = filename[:-4].strip()
        return len(name_part) > 0, filename
    return False, None

def validate_file_path(path) -> tuple[bool, Path | None]:
    if not path.strip():
        return False, None

    path = path.replace('"', '').replace("'", '')

    FilePath = Path(path)
    directory = FilePath.parent
    filename = FilePath.name

    is_dir_valid, DirPath = validate_directory_path(path=str(directory))
    if not is_dir_valid:
        return False, None
    
    is_filename_valid, FileName = validate_csv_filename(filename=filename)
    if not is_filename_valid:
        return False, None
    
    FilePath = DirPath / FileName
    return True, FilePath


def call_export(table, file_path) -> None:
    result = exe.execute_query(sql=TABLE_CONFIG[table]['export_sql'].format(file_path=file_path), header=False, capture=True)

    ff.print_colored(text=f"EXPORT FROM '{TABLE_CONFIG[table]['table_name']}' SUCCESSFUL. {result.stdout.split()[1]} ROWS.\n", color="GREEN")
