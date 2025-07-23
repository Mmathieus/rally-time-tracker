from config import config
import database.others.executor as exe
import utils.formatter as ff
import utils.menu as mm
import utils.inputter as ii
import utils.validator as vv


CREATE_TIMINGS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS timings (
        id SMALLSERIAL PRIMARY KEY,
        rally VARCHAR(25) NOT NULL,
        stage VARCHAR(25) NOT NULL,
        car VARCHAR(25),
        time INTERVAL NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    );
"""

CREATE_TIMINGS_HISTORY_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS timings_history (
        id SMALLINT PRIMARY KEY,
        rally VARCHAR(25) NOT NULL,
        stage VARCHAR(25) NOT NULL,
        car VARCHAR(25),
        time INTERVAL NOT NULL,
        created_at TIMESTAMP
    );
"""

DATABASE_NAME = config['db_connection']['database']
DATABASE_ALIAS = config['operations']['create_refresh_drop']['database_reference']

TIMINGS_ALIAS = config['table_references']['timings']
TIMINGS_HISTORY_ALIAS = config['table_references']['timings_history']

CREATE_AND_DROP_OPTIONS = (TIMINGS_ALIAS, TIMINGS_HISTORY_ALIAS, DATABASE_ALIAS)

DATA_OPTIONS_KEEP = config['operations']['create_refresh_drop']['data_options']['keep']
DATA_OPTIONS = DATA_OPTIONS_KEEP + config['operations']['create_refresh_drop']['data_options']['lose']

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


def _create_exec(what) -> None:
    if what not in CREATE_AND_DROP_OPTIONS:
        return
    
    if what == DATABASE_ALIAS:
        create_database()
    else:
        create_table(table=what)

def create_table(table, confirmation=True) -> None:
    TABLE_NAME = TABLE_CONFIG[table]['table_name']
    
    exists, info_message = vv.validate_db_status(table=TABLE_NAME, must_exist=False)
    if exists:
        ff.print_colored(text=f"TABLE '{TABLE_NAME}' NOT CREATED. {info_message}\n", color="YELLOW")
        return

    exe.execute_query(sql=TABLE_CONFIG[table]['create_sql'], header=False, capture=True)
    
    ff.print_colored(text=f"TABLE '{TABLE_NAME}' CREATED.\n", color="GREEN", really_print=confirmation)
    config['db_status'][TABLE_NAME] = True

def create_database() -> None:
    exists, info_message = vv.validate_db_status(must_exist=False)
    if exists:
        ff.print_colored(text=f"DATABASE '{DATABASE_NAME}' NOT CREATED. {info_message}\n", color="YELLOW")
        return

    exe.execute_query(sql=f"CREATE DATABASE {DATABASE_NAME};", header=False, capture=True, check=False, postgres_db=True)

    ff.print_colored(text=f"DATABASE '{DATABASE_NAME}' CREATED.\n", color="GREEN")
    config['db_status']['database'] = True


def _refresh_manager(table, keep_data=None) -> None:
    if table not in (TIMINGS_ALIAS, TIMINGS_HISTORY_ALIAS):
        ff.print_colored(text=f"INVALID TABLE NAME '{table}'.\n", color="YELLOW")
        return
    
    TABLE_NAME = TABLE_CONFIG[table]['table_name']
    
    exists, info_message = vv.validate_db_status(table=TABLE_NAME)
    if not exists:
        ff.print_colored(text=f"TABLE '{TABLE_NAME}' NOT REFRESHED. {info_message}\n", color="YELLOW")
        return
    
    if not keep_data:
        mm.display_menu(title="KEEP DATA?", options=("Yes", "No"))
        keep_data = ii.get_user_input()
        
    if not vv.validate_choice(choice=keep_data, valid_options=DATA_OPTIONS, choice_type="KEEP DATA"):
        return
    
    refresh_table(table=table, keep_data=keep_data)

def refresh_table(table, keep_data) -> None:
    TABLE_NAME = TABLE_CONFIG[table]['table_name']

    STATUS = "DATA KEPT"
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
        drop_table(table=table, confirmation=False)
        create_table(table=table, confirmation=False)
        STATUS = "DATA LOST"
    
    ff.print_colored(text=f"TABLE '{TABLE_NAME}' REFRESHED. {STATUS}.\n", color="GREEN")


def _drop_exec(what) -> None:
    if what not in CREATE_AND_DROP_OPTIONS:
        return
    
    if what == DATABASE_ALIAS:
        drop_database()
    else:
        drop_table(table=what)

def drop_table(table, confirmation=True) -> None:
    TABLE_NAME = TABLE_CONFIG[table]['table_name']
    beginning = f"TABLE '{TABLE_NAME}'"
    
    exists, info_message = vv.validate_db_status(table=TABLE_NAME)
    if not exists:
        ff.print_colored(text=f"TABLE '{TABLE_NAME}' NOT DROPPED. {info_message}\n", color="YELLOW")
        return

    exe.execute_query(sql=TABLE_CONFIG[table]['drop_sql'], header=False, capture=True)
    
    ff.print_colored(text=f"{beginning} DROPPED.\n", color="GREEN", really_print=confirmation)
    config['db_status'][TABLE_NAME] = False

def drop_database() -> None:
    exists, info_message = vv.validate_db_status()
    if not exists:
        ff.print_colored(text=f"DATABASE '{DATABASE_NAME}' NOT DROPPED. {info_message}\n", color="YELLOW")
        return

    exe.execute_query(sql=f"DROP DATABASE IF EXISTS {DATABASE_NAME};", header=False, capture=True, postgres_db=True)

    ff.print_colored(text=f"DATABASE '{DATABASE_NAME}' DROPPED.\n", color="GREEN")
    config['db_status'] = dict.fromkeys(config['db_status'].keys(), False)
