import config as cnfg

import utils.formatter as ff
import utils.inputter as ii
import utils.menu as mm
import utils.other as oo
import utils.validator as vv

import database.tools.executor as exe
import database.tools.sequence as sqnc

from pathlib import Path
from tkinter import filedialog
import tkinter as tk
import tempfile
import re
import os


DB_NAME = cnfg.config['db_connection']['database']

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

EVERYTHING_ALIAS = cnfg.config['everything_reference']


def import_manager(table, method=None, override=None) -> None:
    if table == EVERYTHING_ALIAS:
        if not method:
            LIMITED_METHOD_OPTIONS = (GUI, DEFAULT)
            mm.display_menu(title="FILE SELECTION?", options=tuple(opt.capitalize() for opt in LIMITED_METHOD_OPTIONS))
            method = ii.get_user_input()

            if not method:
                return

        if method == GUI:
            print()
            _gui_exec(table=TIMINGS_ALIAS, override=override)
            _gui_exec(table=TIMINGS_HISTORY_ALIAS, override=override)
            return
        elif method == DEFAULT:
            print()
            _default_exec(table=TIMINGS_ALIAS, override=override)
            _default_exec(table=TIMINGS_HISTORY_ALIAS, override=override)
            return
        else:
            ff.print_colored(text=f"INVALID CHOICE '{method}'. ONLY '{GUI}' AND '{DEFAULT}' ALLOWED.\n", color="YELLOW")
            return

    if table not in (TIMINGS_ALIAS, TIMINGS_HISTORY_ALIAS):
        ff.print_colored(text=f"INVALID TABLE '{table}'.\n", color="YELLOW")
        return
    
    all_ok, info_message = oo.get_db_exists_state(table=_get_table_name(table=table))
    if not all_ok:
        ff.print_colored(text=f"{_get_unsuccessful_import_message(table=table)} {info_message}\n", color="YELLOW")
        return
    
    if method:
        if method == GUI:
            _gui_exec(table=table, override=override)
        elif method == DEFAULT:
            _default_exec(table=table, override=override)
        else:
            _path_exec(table=table, file_path=method, override=override)
        return

    mm.display_menu(title="FILE SELECTION?", options=tuple(opt.capitalize() for opt in METHOD_OPTIONS))
    method_choice = ii.get_user_input()
    
    if not vv.validate_choice(choice=method_choice, valid_options=METHOD_OPTIONS):
        return
    
    if method_choice == GUI:
        _gui_exec(table=table, override=override)
    elif method_choice == DEFAULT:
        _default_exec(table=table, override=override)
    else:
        file_path = ii.get_user_input(prompt="Enter the full path to the CSV file including the file name and .csv", lowercase=False)
        _path_exec(table=table, file_path=file_path, override=override)


def _gui_exec(table, override) -> None:
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.askopenfilename(
        title=f"Select a CSV file for a table: {_get_table_name(table=table)}",
        filetypes=[("CSV files", "*.csv")]
    )
    
    root.destroy()
    
    if not file_path:
        return
    
    FilePath = Path(file_path)

    _call_import(table=table, file_path=FilePath, override=override)

def _default_exec(table, override) -> None:
    is_valid, FilePath = _validate_file_path(path=TABLE_CONFIG[table]['default_location'].format(database=DB_NAME))
    
    if not is_valid:
        ff.print_colored(text=f"{_get_unsuccessful_import_message(table=table)} INVALID DEFAULT FILE PATH in config.json FOR TABLE '{_get_table_name(table=table)}'.\n", color="YELLOW")
        return
    
    _call_import(table=table, file_path=FilePath, override=override)

def _path_exec(table, file_path, override) -> None:
    is_valid, FilePath = _validate_file_path(path=file_path)

    if not is_valid:
        ff.print_colored(text=f"{_get_unsuccessful_import_message(table=table)} INVALID FILE PATH.\n", color="YELLOW")
        return

    _call_import(table=table, file_path=FilePath, override=override)


def _validate_file_path(path) -> tuple[bool, Path | None]: 
    if not path.strip():
        return False, None
    
    path = path.replace('"', '').replace("'", '')
    
    FilePath = Path(path)
    FilePath = FilePath.resolve()
    
    if not FilePath.exists() or not FilePath.is_file() or FilePath.suffix.lower() != '.csv':
        return False, FilePath
    return True, FilePath

def _call_import(table, file_path, override) -> None:
    doing_override = _should_override(override=override)
    result = None
    override_message = ""

    if doing_override:
        tmp_sql_file = _create_temp_sql_file(table=table, csv_file_path=file_path)
        try:
            result = exe.execute_query(file=tmp_sql_file, header=False, capture=True)
            override_message = "PREVIOUS RECORDS OVERRIDDEN."
        finally:
            if os.path.exists(tmp_sql_file):
                os.remove(tmp_sql_file)
    else:
        import_sql = TABLE_CONFIG[table]['import_sql'].format(file_path=file_path)
        result = exe.execute_query(sql=import_sql, header=False, capture=True, check=False)
    
    if result.stderr:
        if "duplicate key value" in result.stderr.strip():
            duplicate_id = re.search(r'Key\s+\(\w+\)=\((\d+)\)', result.stderr.strip()).group(1)
            ff.print_colored(text=f"{_get_unsuccessful_import_message(table)} DUPLICATE ID '{duplicate_id}' FOUND.\n", color="YELLOW")
            return
        ff.print_colored(text="ERROR IN IMPORT.\n", color="RED")
        return
    
    sqnc.update_sequence()

    imported_rows_count = re.search(r'COPY\s+(\d+)', (result.stdout.strip())).group(1)
    ff.print_colored(
        text=f"IMPORT INTO '{_get_table_name(table)}' SUCCESSFUL. {imported_rows_count} ROWS. {override_message}\n",
        color="GREEN"
    )


def _get_unsuccessful_import_message(table) -> str:
    return f"IMPORT INTO '{_get_table_name(table=table)}' UNSUCCESSFUL."

def _get_table_name(table) -> str:
    return TABLE_CONFIG[table]['table_name']


def _create_temp_sql_file(table, csv_file_path) -> str:
    TABLE_NAME = _get_table_name(table=table)
    
    sql_content = (
        f"BEGIN;\n"
        f"DELETE FROM {TABLE_NAME};\n"
        f"\\copy {TABLE_NAME} FROM '{csv_file_path}' WITH (FORMAT csv);\n"
        f"COMMIT;\n"
    )

    tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8')
    tmp_file.write(sql_content)
    tmp_file.close()
    return tmp_file.name

def _should_override(override) -> bool:
    if override:
        return vv.validate_choice(
            choice=override,
            valid_options=cnfg.config['operations']['import_export']['override_data_options'],
            print_error=False
        )
    return cnfg.config['operations']['import_export']['override_data_on_import']
