import config as cnfg

import utils.formatter as ff
import utils.other as oo

import database.tools.executor as exe

from pathlib import Path
import re


CREATE__DROP_OPTIONS = (cnfg.PRIMARY_TB_ALIAS, cnfg.HISTORY_TB_ALIAS, cnfg.DB_ALIAS)

TABLE_CONFIG = {
    cnfg.PRIMARY_TB_ALIAS: {
        'create_sql_file_path': Path(__file__).parent / "ddl" / "primary.sql",
        'drop_sql': "DROP TABLE IF EXISTS timings;"
    },
    cnfg.HISTORY_TB_ALIAS: {
        'create_sql_file_path': Path(__file__).parent / "ddl" / "history.sql",
        'drop_sql': "DROP TABLE IF EXISTS timings_history;"
    }
}


def create_exec(target) -> None:
    if target == cnfg.EVERYTHING_ALIAS:
        print()
        _create_database()
        create_table(table=cnfg.PRIMARY_TB_ALIAS)
        create_table(table=cnfg.HISTORY_TB_ALIAS)
        return
    
    if target not in CREATE__DROP_OPTIONS:
        ff.print_colored(text=f"INVALID CREATE CHOICE '{target}'.\n", color="RED")
        return
    
    if target == cnfg.DB_ALIAS:
        _create_database()
    else:
        create_table(table=target)

def create_table(table, print_confirmation=True) -> None:
    # Check if DB/TABLE exists
    all_ok, info_message = oo.get_db_exists_state(table=cnfg.get_tb_name(table=table), must_exists=False)
    if not all_ok:
        ff.print_colored(text=f"TABLE '{cnfg.get_tb_name(table=table)}' NOT CREATED. {info_message}\n", color="YELLOW")
        return

    exe.execute_query(file=TABLE_CONFIG[table]['create_sql_file_path'], header=False, capture=True)
    
    ff.print_colored(text=f"TABLE '{cnfg.get_tb_name(table=table)}' CREATED.\n", color="GREEN", really_print=print_confirmation)
    
    _set_exists_status(target=cnfg.get_tb_name(table=table), new_value=True)

def _create_database() -> None:
    # Check if DB/TABLE exists
    all_ok, info_message = oo.get_db_exists_state(must_exists=False)
    if not all_ok:
        ff.print_colored(text=f"DATABASE '{cnfg.DB_NAME}' NOT CREATED. {info_message}\n", color="YELLOW")
        return

    exe.execute_query(sql=f"CREATE DATABASE {cnfg.DB_NAME};", header=False, capture=True, postgres_db=True)

    ff.print_colored(text=f"DATABASE '{cnfg.DB_NAME}' CREATED.\n", color="GREEN")
    
    _set_exists_status(target="database", new_value=True)


def drop_exec(target) -> None:
    if target == cnfg.EVERYTHING_ALIAS:
        _drop_database()
        return
    
    if target == cnfg.TABLES_ALIAS:
        print()
        drop_table(cnfg.PRIMARY_TB_ALIAS)
        drop_table(cnfg.HISTORY_TB_ALIAS)
        return

    if target not in CREATE__DROP_OPTIONS:
        ff.print_colored(text=f"INVALID DROP CHOICE '{target}'.\n", color="RED")
        return
    
    if target == cnfg.DB_ALIAS:
        _drop_database()
    else:
        drop_table(table=target)

def drop_table(table, print_confirmation=True) -> None:
    # Check if DB/TABLE exists
    all_ok, info_message = oo.get_db_exists_state(table=cnfg.get_tb_name(table=table))
    if not all_ok:
        ff.print_colored(text=f"TABLE '{cnfg.get_tb_name(table=table)}' NOT DROPPED. {info_message}\n", color="YELLOW")
        return

    exe.execute_query(sql=TABLE_CONFIG[table]['drop_sql'], header=False, capture=True)
    
    ff.print_colored(text=f"TABLE '{cnfg.get_tb_name(table=table)}' DROPPED.\n", color="GREEN", really_print=print_confirmation)
    
    _set_exists_status(target=cnfg.get_tb_name(table=table), new_value=False)

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
