from config import config
import utils.inputter as ii
import utils.formatter as ff
import utils.menu as mm
import utils.validator as vv
import database.others.executor as exe

from pathlib import Path
import tkinter as tk
from tkinter import filedialog


TIMINGS_ALIAS = config['table_references']['timings']
TIMINGS_HISTORY_ALIAS = config['table_references']['timings_history']

GUI = config['operations']['import_export']['file_selection_options']['GUI']
DEFAULT = config['operations']['import_export']['file_selection_options']['Default']
PATH = config['operations']['import_export']['file_selection_options']['Path']

FILE_SELECTION_OPTIONS = (GUI, DEFAULT, PATH)

TABLE_CONFIG = {
    TIMINGS_ALIAS: {
        'table_name': "timings",
        'import_sql': "\\copy timings FROM '{file_path}' WITH (FORMAT csv);",
        'default_location': config['default_import_locations']['timings']
    },
    TIMINGS_HISTORY_ALIAS: {
        'table_name': "timings_history",
        'import_sql': "\\copy timings_history FROM '{file_path}' WITH (FORMAT csv);",
        'default_location': config['default_import_locations']['timings_history']
    }
}


def _import_manager(table, file_selection=None) -> None:
    if table not in (TIMINGS_ALIAS, TIMINGS_HISTORY_ALIAS):
        ff.print_colored(text=f"INVALID TABLE '{table}'.\n", color="YELLOW")
        return
    
    TABLE_NAME = TABLE_CONFIG[table]['table_name']
    
    exists, info_message = vv.validate_db_status(table=TABLE_NAME)
    if not exists:
        ff.print_colored(text=f"IMPORT INTO '{TABLE_NAME}' UNSUCCESSFUL. {info_message}\n", color="YELLOW")
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
    
    file_path = filedialog.askopenfilename(
        title="Select a CSV file",
        filetypes=[("CSV files", "*.csv")]
    )
    
    root.destroy()
    
    if not file_path:
        return
    
    FilePath = Path(file_path)

    call_import(table=table, file_path=FilePath)

def default_exec(table) -> None:
    is_valid, FilePath = validate_file_path(path=TABLE_CONFIG[table]['default_location'])
    
    if not is_valid:
        ff.print_colored(text=f"INVALID DEFAULT FILE PATH in config.json FOR TABLE '{TABLE_CONFIG[table]['table_name']}'.\n", color="YELLOW")
        return
    
    call_import(table=table, file_path=FilePath)

def path_exec(table, file_path) -> None:
    is_valid, FilePath = validate_file_path(path=file_path)

    if not is_valid:
        ff.print_colored(text=f"INVALID FILE PATH.\n", color="YELLOW")
        return

    call_import(table=table, file_path=FilePath)


def validate_file_path(path) -> tuple[bool, Path | None]: 
    if not path.strip():
        return False, None
    
    path = path.replace('"', '').replace("'", '')
    
    FilePath = Path(path)
    FilePath = FilePath.resolve()
    
    if not FilePath.exists() or not FilePath.is_file() or FilePath.suffix.lower() != '.csv':
        return False, FilePath
    return True, FilePath

def call_import(table, file_path) -> None:
    result = exe.execute_query(sql=TABLE_CONFIG[table]['import_sql'].format(file_path=file_path), header=False, capture=True)

    ff.print_colored(text=f"IMPORT INTO '{TABLE_CONFIG[table]['table_name']}' SUCCESSFUL. {result.stdout.split()[1]} ROWS.\n", color="GREEN")
