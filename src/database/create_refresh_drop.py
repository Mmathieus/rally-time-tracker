from config import config
import database.others.executor as exe
import utils.formatter as ff
import utils.menu as mm
import utils.inputter as ii


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

TIMINGS_ALIAS = config['table_references']['timings']
TIMINGS_HISTORY_ALIAS = config['table_references']['timings_history']

TABLE_OPTIONS = (TIMINGS_ALIAS, TIMINGS_HISTORY_ALIAS)

CREATE_AND_DROP_OPTIONS = (TIMINGS_ALIAS, TIMINGS_HISTORY_ALIAS, "db")

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
    
    if what == "db":
        create_database()
    else:
        create_table(table=what)

def create_table(table, confirmation=True) -> None:
    answer = exe.execute_query(sql=TABLE_CONFIG[table]['create_sql'], header=False, capture=True)
    
    output = f"TABLE '{TABLE_CONFIG[table]['table_name']}'"
    
    if answer.stderr and "already exists" in answer.stderr.strip():
        ff.print_colored(text=f"{output} NOT CREATED - ALREADY EXISTS.\n", color="YELLOW")
        return
    
    ff.print_colored(text=f"{output} CREATED.\n", color="GREEN", really_print=confirmation)

def create_database() -> None:
    query = f"CREATE DATABASE {DATABASE_NAME}"

    answer = exe.execute_query(sql=query, header=False, capture=True, check=False, postgres_db=True)

    if answer.stderr and "already exists" in answer.stderr.strip():
        ff.print_colored(text=f"DATABASE '{DATABASE_NAME}' NOT CREATED - ALREADY EXISTS.\n", color="YELLOW")
        return

    ff.print_colored(text=f"DATABASE '{DATABASE_NAME}' CREATED.\n", color="GREEN")


def _refresh_manager(table, keep_data=None) -> None:
    if table not in TABLE_OPTIONS:
        ff.print_colored(text=f"INVALID TABLE NAME '{table}'.\n", color="YELLOW")
        return
    
    if not keep_data:
        mm.display_menu(title="KEEP DATA?", options=("Yes", "No"))
        keep_data = ii.get_user_input()
        
    if not validate_choice(choice=keep_data, valid_options=('y', 'n', "yes", "no", "keep", "lose"), choice_type="KEEP DATA"):
        return
    
    refresh_table(table=table, keep_data=keep_data)

def refresh_table(table, keep_data) -> None:
    table_name = TABLE_CONFIG[table]['table_name']

    exists = exe.execute_query(
        sql=f"SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = '{table_name}');",
        header=False,
        capture=True
    )
    
    if exists.stdout.strip() == 'f':
        ff.print_colored(text=f"TABLE '{table_name}' NOT REFRESHED - DOESN'T EXIST.\n", color="YELLOW")
        return
    
    if keep_data.startswith('y') or keep_data == "keep":
        transaction = f"""
            BEGIN;
            
            CREATE TEMP TABLE {table_name}_backup AS SELECT * FROM {table_name};
            {TABLE_CONFIG[table]['drop_sql']}
            {TABLE_CONFIG[table]['create_sql']}
            INSERT INTO {table_name} SELECT * FROM {table_name}_backup;
            
            COMMIT;
        """
        exe.execute_query(sql=transaction, header=False, capture=True)
    else:
        drop_table(table=table, confirmation=False)
        create_table(table=table, confirmation=False)
    
    ff.print_colored(text=f"TABLE '{table_name}' REFRESHED.\n", color="GREEN")


def _drop_exec(what) -> None:
    if what not in CREATE_AND_DROP_OPTIONS:
        return
    
    if what == "db":
        drop_database()
    else:
        drop_table(table=what)

def drop_table(table, confirmation=True) -> None:
    answer = exe.execute_query(sql=TABLE_CONFIG[table]['drop_sql'], header=False, capture=True)
    
    output = f"TABLE '{TABLE_CONFIG[table]['table_name']}'"
    
    if answer.stderr and "does not exist" in answer.stderr.strip():
        ff.print_colored(text=f"{output} NOT DROPPED - DOESN'T EXIST.\n", color="YELLOW")
        return
    
    ff.print_colored(text=f"{output} DROPPED.\n", color="GREEN", really_print=confirmation)

def drop_database() -> None:
    query = f"DROP DATABASE IF EXISTS {DATABASE_NAME};"

    answer = exe.execute_query(sql=query, header=False, capture=True, postgres_db=True)

    if answer.stderr and "does not exist" in answer.stderr.strip():
        ff.print_colored(text=f"DATABASE '{DATABASE_NAME}' NOT DROPPED - DOESN'T EXIST.\n", color="YELLOW")
        return

    ff.print_colored(text=f"DATABASE '{DATABASE_NAME}' DROPPED.\n", color="GREEN")



def validate_choice(choice, valid_options, choice_type) -> bool:
    """Validate user choice against valid options."""
    if not choice:
        return False
    
    if choice not in valid_options:
        ff.print_colored(text=f"INVALID {choice_type} CHOICE.\n", color="RED")
        return False
    
    return True
