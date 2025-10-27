import config as cnfg

import utils.formatter as ff
import utils.inputter as ii
import utils.validator as vv
import utils.other as u_othr

import database.tools.executor as exe
import database.tools.state as stt

from pathlib import Path
from tkinter import filedialog
import tkinter as tk
import re


GUI = cnfg.config['command']['import__export']['location_selection']['GUI'].strip()
DEFAULT = cnfg.config['command']['import__export']['location_selection']['Default'].strip()

METHOD_OPTIONS = (GUI, DEFAULT)

TABLE_CONFIG = {
    cnfg.PRIMARY_TB_ALIAS: {
        'export_sql': "\\copy timings TO '{file_path}' WITH (FORMAT csv);",
        'default_location': cnfg.config['command']['export']['default_folder_path']['primary_table'].strip(),
        'default_file_name': cnfg.config['command']['export']['default_file_name']['primary_table'].strip()
    },
    cnfg.HISTORY_TB_ALIAS: {
        'export_sql': "\\copy timings_history TO '{file_path}' WITH (FORMAT csv);",
        'default_location': cnfg.config['command']['export']['default_folder_path']['history_table'].strip(),
        'default_file_name': cnfg.config['command']['export']['default_file_name']['history_table'].strip()
    }
}


def export_manager(table, method=None) -> None:
    # Export on both tables
    if table == cnfg.EVERYTHING_ALIAS:
        
        # Check if DB/TABLES exist
        if not stt.verify_db_exists_state(bad_info_message=ff.colorize(text="EXPORT NOT POSSIBLE. {rest}\n", color="YELLOW")):
            return

        # Determine 'method' value
        method = _determine_method(method=method)
        if not method:
            return
        
        print()
        # GUI
        if method == GUI:
            export_manager(table=cnfg.PRIMARY_TB_ALIAS, method=GUI)
            export_manager(table=cnfg.HISTORY_TB_ALIAS, method=GUI)
        # DEFAULT
        else:
            export_manager(table=cnfg.PRIMARY_TB_ALIAS, method=DEFAULT)
            export_manager(table=cnfg.HISTORY_TB_ALIAS, method=DEFAULT)
        return



    # Check table name
    if table not in cnfg.BOTH_TABLES:
        ff.print_colored(text=f"INVALID TABLE '{table}'.\n", color="RED")
        return
    
    # Check if DB/TABLE exists
    if not stt.check_db_exists_state(
        table=cnfg.get_tb_name(table=table),
        info_message=ff.colorize(text="EXPORT NOT POSSIBLE. {rest}\n", color="YELLOW")
    )[0]:
        return

    
    # Determine 'method' value
    method = _determine_method(method=method)
    if not method:
        return
    

    # GUI
    if method == GUI:
        _gui_exec(table=table)
    # DEFAULT
    else:
        _default_exec(table=table)


def _gui_exec(table) -> None:
    root = tk.Tk()
    root.withdraw()
    
    # GUI selector
    directory_path = filedialog.askdirectory(
        title=f"Select directory to save the file from table: {cnfg.get_tb_name(table=table)}"
    )
    
    root.destroy()
    
    # Cancelled folder path selection
    if not directory_path:
        print()
        return
    
    # Validating file name (*.csv) from config.json
    FileName = _validate_csv_filename(filename=TABLE_CONFIG[table]['default_file_name'])
    if not FileName:
        ff.print_colored(text=f"{_get_unsuccessful_export_message(table=table)} INVALID DEFAULT FILENAME in config.json FOR TABLE '{cnfg.get_tb_name(table=table)}'.\n", color="YELLOW")
        return
    
    FilePath = Path(directory_path) / FileName

    _call_export(table=table, file_path=FilePath)

def _default_exec(table) -> None:
    # Validating folder path. {database} must be included in folder path, in config.json
    DirPath = _validate_directory_path(path=TABLE_CONFIG[table]['default_location'].format(database=cnfg.DB_NAME), table=table, simple_validation=False)
    
    if not DirPath:
        ff.print_colored(text=f"{_get_unsuccessful_export_message(table=table)} INVALID DEFAULT DIRECTORY PATH in config.json FOR TABLE '{cnfg.get_tb_name(table=table)}'.\n", color="YELLOW")
        return
    
    # Validating file name
    FileName = _validate_csv_filename(filename=TABLE_CONFIG[table]['default_file_name'])
    
    if not FileName:
        ff.print_colored(text=f"{_get_unsuccessful_export_message(table=table)} INVALID DEFAULT FILENAME in config.json FOR TABLE '{cnfg.get_tb_name(table=table)}'.\n", color="YELLOW")
        return
    
    FilePath = DirPath / FileName
    
    _call_export(table=table, file_path=FilePath)


def _call_export(table, file_path) -> None:
    result = exe.execute_query(sql=TABLE_CONFIG[table]['export_sql'].format(file_path=file_path), header=False, capture=True)

    ff.print_colored(text=f"EXPORT FROM '{cnfg.get_tb_name(table=table)}' SUCCESSFUL. {result.stdout.split()[1]} ROWS.\n", color="GREEN")


def _validate_directory_path(path, table, simple_validation=True) -> Path | None: 
    # No path
    if not path.strip():
        return None
    
    # Quotation marks removed
    path = path.replace('"', '').replace("'", '')
    
    DirPath = Path(path)
    DirPath = DirPath.resolve()

    # PATH from config.json with {}
    if not simple_validation:
        # Parent doesn't exist -> instant return
        if not DirPath.parent.exists() or not DirPath.parent.is_dir():
            return None
        
        try:
            DirPath.mkdir(exist_ok=True)
        except Exception:
            ff.print_colored(text=f"FAILED TO CREATE EXPORT DIRECTORY FOR DATABASE '{cnfg.DB_NAME}' TABLE '{cnfg.get_tb_name(table=table)}'", color="RED")
            return None

    if not DirPath.exists() or not DirPath.is_dir():
        return None

    return DirPath

def _validate_csv_filename(filename) -> str | None:
    # At least one character as file name + .csv
    pattern = r'^.+\.csv$'
    filename = filename.strip()
    
    # Validate file format and file name
    if re.match(pattern, filename, re.IGNORECASE) and len(filename[:-4].strip()) > 0:
        return filename
    return None


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


def _get_unsuccessful_export_message(table) -> str:
    return f"EXPORT FROM '{cnfg.get_tb_name(table=table)}' UNSUCCESSFUL."
