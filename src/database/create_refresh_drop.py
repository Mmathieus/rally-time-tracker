import config as cnfg

import utils.formatter as ff
import utils.inputter as ii
import utils.menu as mm
import utils.other as oo
import utils.validator as vv

import database.tools.executor as exe
import database.tools.sequence as sqnc

import re


CREATE_TIMINGS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS timings (
        id SMALLSERIAL PRIMARY KEY,
        rally VARCHAR(126) NOT NULL,
        stage VARCHAR(126) NOT NULL,
        car VARCHAR(126),
        time INTERVAL NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
"""

CREATE_TIMINGS_HISTORY_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS timings_history (
        id SMALLINT PRIMARY KEY,
        rally VARCHAR(126) NOT NULL,
        stage VARCHAR(126) NOT NULL,
        car VARCHAR(126),
        time INTERVAL NOT NULL,
        created_at TIMESTAMP NOT NULL
    );
"""

DATABASE_NAME = cnfg.config['db_connection']['database']
DATABASE_ALIAS = cnfg.config['operations']['create_refresh_drop']['database_reference']

TIMINGS_ALIAS = cnfg.config['table_references']['timings']
TIMINGS_HISTORY_ALIAS = cnfg.config['table_references']['timings_history']

CREATE_AND_DROP_OPTIONS = (TIMINGS_ALIAS, TIMINGS_HISTORY_ALIAS, DATABASE_ALIAS)

DATA_OPTIONS_KEEP = cnfg.config['operations']['create_refresh_drop']['data_options']['keep']
DATA_OPTIONS = DATA_OPTIONS_KEEP + cnfg.config['operations']['create_refresh_drop']['data_options']['lose']

TABLE_CONFIG = {
    TIMINGS_ALIAS: {
        'table_name': "timings",
        'create_sql': CREATE_TIMINGS_TABLE_SQL,
        'drop_sql': "DROP TABLE IF EXISTS timings;"
    },
    TIMINGS_HISTORY_ALIAS: {
        'table_name': "timings_history",
        'create_sql': CREATE_TIMINGS_HISTORY_TABLE_SQL,
        'drop_sql': "DROP TABLE IF EXISTS timings_history;"
    }
}


def create_exec(target) -> None:
    if target not in CREATE_AND_DROP_OPTIONS:
        return
    
    if target == DATABASE_ALIAS:
        _create_database()
    else:
        _create_table(table=target)

def _create_table(table, print_confirmation=True) -> None:
    TABLE_NAME = TABLE_CONFIG[table]['table_name']
    
    all_ok, info_message = oo.get_db_exists_state(table=TABLE_NAME, must_exists=False)
    if not all_ok:
        ff.print_colored(text=f"TABLE '{TABLE_NAME}' NOT CREATED. {info_message}\n", color="YELLOW")
        return

    exe.execute_query(sql=TABLE_CONFIG[table]['create_sql'], header=False, capture=True)
    
    ff.print_colored(text=f"TABLE '{TABLE_NAME}' CREATED.\n", color="GREEN", really_print=print_confirmation)
    _set_exists_status(target=TABLE_NAME, new_value=True)

def _create_database() -> None:
    all_ok, info_message = oo.get_db_exists_state(must_exists=False)
    if not all_ok:
        ff.print_colored(text=f"DATABASE '{DATABASE_NAME}' NOT CREATED. {info_message}\n", color="YELLOW")
        return

    exe.execute_query(sql=f"CREATE DATABASE {DATABASE_NAME};", header=False, capture=True, check=False, postgres_db=True)

    ff.print_colored(text=f"DATABASE '{DATABASE_NAME}' CREATED.\n", color="GREEN")
    _set_exists_status(target="database", new_value=True)


def refresh_manager(table, keep_data=None) -> None:
    if table not in (TIMINGS_ALIAS, TIMINGS_HISTORY_ALIAS):
        ff.print_colored(text=f"INVALID TABLE NAME '{table}'.\n", color="YELLOW")
        return
    
    TABLE_NAME = TABLE_CONFIG[table]['table_name']
    
    all_ok, info_message = oo.get_db_exists_state(table=TABLE_NAME)
    if not all_ok:
        ff.print_colored(text=f"TABLE '{TABLE_NAME}' NOT REFRESHED. {info_message}\n", color="YELLOW")
        return
    
    if not keep_data:
        mm.display_menu(title="KEEP DATA?", options=("Yes", "No"))
        keep_data = ii.get_user_input()
        
    if not vv.validate_choice(choice=keep_data, valid_options=DATA_OPTIONS):
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
            {TABLE_CONFIG[table]['create_sql']}
            INSERT INTO {TABLE_NAME} SELECT * FROM {TABLE_NAME}_backup;
            
            COMMIT;
        """
        exe.execute_query(sql=transaction, header=False, capture=True)
    else:
        _drop_table(table=table, print_confirmation=False)
        _create_table(table=table, print_confirmation=False)
        data_status = "DATA LOST."
    
    ff.print_colored(text=f"TABLE '{TABLE_NAME}' REFRESHED. {data_status}\n", color="GREEN")

    sqnc.update_sequence()


def drop_exec(target) -> None:
    if target not in CREATE_AND_DROP_OPTIONS:
        return
    
    if target == DATABASE_ALIAS:
        _drop_database()
    else:
        _drop_table(table=target)

def _drop_table(table, print_confirmation=True) -> None:
    TABLE_NAME = TABLE_CONFIG[table]['table_name']
    beginning = f"TABLE '{TABLE_NAME}'"
    
    all_ok, info_message = oo.get_db_exists_state(table=TABLE_NAME)
    if not all_ok:
        ff.print_colored(text=f"{beginning} NOT DROPPED. {info_message}\n", color="YELLOW")
        return

    exe.execute_query(sql=TABLE_CONFIG[table]['drop_sql'], header=False, capture=True)
    
    ff.print_colored(text=f"{beginning} DROPPED.\n", color="GREEN", really_print=print_confirmation)
    _set_exists_status(target=TABLE_NAME, new_value=False)

def _drop_database() -> None:
    all_ok, info_message = oo.get_db_exists_state()
    if not all_ok:
        ff.print_colored(text=f"DATABASE '{DATABASE_NAME}' NOT DROPPED. {info_message}\n", color="YELLOW")
        return

    result = exe.execute_query(sql=f"DROP DATABASE IF EXISTS {DATABASE_NAME};", header=False, capture=True, postgres_db=True, check=False)

    psql_message = result.stderr.strip()

    if "is being accessed" in psql_message:
        sessions_count = int(re.search(r'DETAIL:.*?(\d+)', psql_message).group(1))
        session_text = "OTHER SESSION IS" if sessions_count == 1 else "OTHER SESSIONS ARE"

        ff.print_colored(text=f"DATABASE '{DATABASE_NAME}' NOT DROPPED. {sessions_count} {session_text} USING THIS DATABASE.\n", color="YELLOW")
        return

    ff.print_colored(text=f"DATABASE '{DATABASE_NAME}' DROPPED.\n", color="GREEN")
    _set_exists_status(new_value=False)


def _set_exists_status(target="all", new_value=None) -> None:
    if target == "all":
        for k in cnfg.db_state:
            cnfg.db_state[k]['exists'] = new_value
    elif isinstance(target, str):
        cnfg.db_state[target]['exists'] = new_value
    elif isinstance(target, tuple):
        for k in target:
            cnfg.db_state[k]['exists'] = new_value
    else:
        ff.print_colored(text="PROGRAM INFO : PARAMETER 'target' IS WRONG TYPE.\n", color="RED")
