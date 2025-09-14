import config as cnfg

import utils.formatter as ff
import utils.other as oo
import utils.validator as vv

import database.tools.executor as exe
import database.tools.sequence as sqnc
import database.tools.tmp_file as tmpfl

from pathlib import Path
import os
import re


DATABASE_ALIAS = cnfg.config['operations']['create_refresh_drop']['database_reference']

ALL_TABLES_ALIAS = cnfg.config['operations']['create_refresh_drop']['all_tables_reference']

CREATE_AND_DROP_OPTIONS = (cnfg.TIMINGS_ALIAS, cnfg.TIMINGS_HISTORY_ALIAS, DATABASE_ALIAS)

DATA_OPTIONS_KEEP = cnfg.config['operations']['create_refresh_drop']['data_options']['keep']
DATA_OPTIONS_LOSE = cnfg.config['operations']['create_refresh_drop']['data_options']['lose']
DATA_OPTIONS = DATA_OPTIONS_KEEP + DATA_OPTIONS_LOSE

TABLE_CONFIG = {
    cnfg.TIMINGS_ALIAS: {
        'table_name': cnfg.TIMINGS_REAL,
        'create_sql_file_path': Path(__file__).parent / "ddl" / "timings.sql",
        'drop_sql': "DROP TABLE IF EXISTS timings;"
    },
    cnfg.TIMINGS_HISTORY_ALIAS: {
        'table_name': cnfg.TIMINGS_HISTORY_REAL,
        'create_sql_file_path': Path(__file__).parent / "ddl" / "timings_history.sql",
        'drop_sql': "DROP TABLE IF EXISTS timings_history;"
    }
}


def create_exec(target) -> None:
    if target == cnfg.EVERYTHING_ALIAS:
        print()
        _create_database()
        _create_table(table=cnfg.TIMINGS_ALIAS)
        _create_table(table=cnfg.TIMINGS_HISTORY_ALIAS)
        return
    
    if target not in CREATE_AND_DROP_OPTIONS:
        ff.print_colored(text=f"INVALID CREATE CHOICE '{target}'.\n", color="RED")
        return
    
    if target == DATABASE_ALIAS:
        _create_database()
    else:
        _create_table(table=target)

def _create_table(table, print_confirmation=True) -> None:
    TABLE_NAME = TABLE_CONFIG[table]['table_name']
    
    # Check if DB/TABLE exists
    all_ok, info_message = oo.get_db_exists_state(table=TABLE_NAME, must_exists=False)
    if not all_ok:
        ff.print_colored(text=f"TABLE '{TABLE_NAME}' NOT CREATED. {info_message}\n", color="YELLOW")
        return

    exe.execute_query(file=TABLE_CONFIG[table]['create_sql_file_path'], header=False, capture=True)
    
    ff.print_colored(text=f"TABLE '{TABLE_NAME}' CREATED.\n", color="GREEN", really_print=print_confirmation)
    
    _set_exists_status(target=TABLE_NAME, new_value=True)

def _create_database() -> None:
    # Check if DB/TABLE exists
    all_ok, info_message = oo.get_db_exists_state(must_exists=False)
    if not all_ok:
        ff.print_colored(text=f"DATABASE '{cnfg.DB_NAME}' NOT CREATED. {info_message}\n", color="YELLOW")
        return

    exe.execute_query(sql=f"CREATE DATABASE {cnfg.DB_NAME};", header=False, capture=True, postgres_db=True)

    ff.print_colored(text=f"DATABASE '{cnfg.DB_NAME}' CREATED.\n", color="GREEN")
    
    _set_exists_status(target="database", new_value=True)


def refresh_manager(table, keep_data=None) -> None:
    if table not in (cnfg.TIMINGS_ALIAS, cnfg.TIMINGS_HISTORY_ALIAS):
        ff.print_colored(text=f"INVALID TABLE NAME '{table}'.\n", color="YELLOW")
        return
    
    TABLE_NAME = TABLE_CONFIG[table]['table_name']
    
    # Check if DB/TABLE exists
    all_ok, info_message = oo.get_db_exists_state(table=TABLE_NAME)
    if not all_ok:
        ff.print_colored(text=f"TABLE '{TABLE_NAME}' NOT REFRESHED. {info_message}\n", color="YELLOW")
        return
    
    if not keep_data:
        DEFAULT_KEEP_DATA = cnfg.config['operations']['create_refresh_drop']['keep_data_on_refresh']
        keep_data = DATA_OPTIONS_KEEP[0] if DEFAULT_KEEP_DATA else DATA_OPTIONS_LOSE[0]
    
    validated, validation_message = vv.validate_choice(choice=keep_data, valid_options=DATA_OPTIONS, choice_name="KEEP_DATA")
    if not validated:
        ff.print_colored(text=f"{validation_message}\n", color="RED")
        return
    
    _refresh_table(table=table, keep_data=keep_data)

def _refresh_table(table, keep_data) -> None:
    TABLE_NAME = TABLE_CONFIG[table]['table_name']

    data_status = "DATA KEPT."
    
    if keep_data in DATA_OPTIONS_KEEP:
        transaction = f"""
            BEGIN;
                CREATE TEMP TABLE {TABLE_NAME}_backup AS SELECT * FROM {TABLE_NAME};
                {TABLE_CONFIG[table]['drop_sql']}
                \\i '{TABLE_CONFIG[table]['create_sql_file_path'].as_posix()}';
                INSERT INTO {TABLE_NAME} SELECT * FROM {TABLE_NAME}_backup;
            COMMIT;
        """

        tmp_sql_file = tmpfl.create_tmp_sql_file(sql_content=transaction)

        try:
            exe.execute_query(file=tmp_sql_file, header=False, capture=True)
        finally:
            if os.path.exists(tmp_sql_file):
                os.remove(tmp_sql_file)
    else:
        _drop_table(table=table, print_confirmation=False)
        _create_table(table=table, print_confirmation=False)
        data_status = "DATA LOST."
    
    sqnc.update_sequence()

    ff.print_colored(text=f"TABLE '{TABLE_NAME}' REFRESHED. {data_status}\n", color="GREEN")


def drop_exec(target) -> None:
    if target == cnfg.EVERYTHING_ALIAS:
        print()
        _drop_database()
        return
    
    if target == ALL_TABLES_ALIAS:
        print()
        _drop_table(cnfg.TIMINGS_ALIAS)
        _drop_table(cnfg.TIMINGS_HISTORY_ALIAS)
        return

    if target not in CREATE_AND_DROP_OPTIONS:
        ff.print_colored(text=f"INVALID DROP CHOICE '{target}'.\n", color="RED")
        return
    
    if target == DATABASE_ALIAS:
        _drop_database()
    else:
        _drop_table(table=target)

def _drop_table(table, print_confirmation=True) -> None:
    TABLE_NAME = TABLE_CONFIG[table]['table_name']
    
    # Check if DB/TABLE exists
    all_ok, info_message = oo.get_db_exists_state(table=TABLE_NAME)
    if not all_ok:
        ff.print_colored(text=f"TABLE '{TABLE_NAME}' NOT DROPPED. {info_message}\n", color="YELLOW")
        return

    exe.execute_query(sql=TABLE_CONFIG[table]['drop_sql'], header=False, capture=True)
    
    ff.print_colored(text=f"TABLE '{TABLE_NAME}' DROPPED.\n", color="GREEN", really_print=print_confirmation)
    
    _set_exists_status(target=TABLE_NAME, new_value=False)

def _drop_database() -> None:
    # Check if DB/TABLE exists
    all_ok, info_message = oo.get_db_exists_state()
    if not all_ok:
        ff.print_colored(text=f"DATABASE '{cnfg.DB_NAME}' NOT DROPPED. {info_message}\n", color="YELLOW")
        return

    result = exe.execute_query(sql=f"DROP DATABASE IF EXISTS {cnfg.DB_NAME};", header=False, capture=True, postgres_db=True, check=False)

    psql_message = result.stderr.strip()

    if "is being accessed" in psql_message:
        sessions_count = int(re.search(r'DETAIL:.*?(\d+)', psql_message).group(1))
        session_text = "OTHER SESSION IS" if sessions_count == 1 else "OTHER SESSIONS ARE"

        ff.print_colored(text=f"DATABASE '{cnfg.DB_NAME}' NOT DROPPED. {sessions_count} {session_text} USING THIS DATABASE.\n", color="YELLOW")
        return

    ff.print_colored(text=f"DATABASE '{cnfg.DB_NAME}' DROPPED.\n", color="GREEN")
    
    _set_exists_status(target="all", new_value=False)


def _set_exists_status(target="all", new_value=None) -> None:
    if target == "all":
        for k in cnfg.db_state:
            cnfg.db_state[k]['exists'] = new_value
    elif isinstance(target, str):
        cnfg.db_state[target]['exists'] = new_value
    else:
        ff.print_colored(text="PROGRAM INFO : PARAMETER 'target' IS WRONG TYPE.\n", color="RED")
