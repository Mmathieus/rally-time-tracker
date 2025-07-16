from config import config
from database import executor as exe
from utils import formatter as ff, visualizer as vv


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

TIMINGS_ALIAS = config['table_references']['timings']
TIMINGS_HISTORY_ALIAS = config['table_references']['timings_history']
BOTH_TIMINGS_ALIAS = config['table_references']['timings & timings_history']

TABLE_OPTIONS = (TIMINGS_ALIAS, TIMINGS_HISTORY_ALIAS, BOTH_TIMINGS_ALIAS)

OPERATION_OPTIONS = ("Create", "Refresh", "Delete")

KEEP_DATA_CHOICES = ('y', 'n', "yes", "no", "keep", "lose")


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


def validate_choice(choice, valid_options, choice_type) -> bool:
    """Validate user choice against valid options."""
    if not choice:
        return False
    
    if choice not in valid_options:
        ff.print_colored(text=f"INVALID {choice_type} CHOICE.\n", color="RED")
        return False
    
    return True


def _setup_manager(table_choice=None, operation_choice=None, keep_data_choice=None) -> None:
    if not table_choice:
        table_choice = vv.get_input__display_menu(title="TABLE OPTIONS", options=tuple(tab.capitalize() for tab in TABLE_OPTIONS))
    
    if not validate_choice(choice=table_choice, valid_options=TABLE_OPTIONS, choice_type="TABLE"):
        return


    if not operation_choice:
        operation_choice = vv.get_input__display_menu(title="OPERATION OPTIONS", options=OPERATION_OPTIONS)
    
    if not validate_choice(choice=operation_choice, valid_options=tuple(op.lower() for op in OPERATION_OPTIONS), choice_type="OPERATION"):
        return


    if operation_choice == "refresh":
        if not keep_data_choice:
            keep_data_choice = vv.get_input__display_menu(title="KEEP DATA?", options=("Yes", "No"))
        
        if not validate_choice(choice=keep_data_choice, valid_options=KEEP_DATA_CHOICES, choice_type="KEEP DATA"):
            return
    
    _setup_exec(table=table_choice, operation=operation_choice, keep_data=keep_data_choice)


def _setup_exec(table, operation, keep_data) -> None:
    if operation == "create":
        create_table(table=table)
        return

    if operation == "refresh":
        refresh_table(table=table, keep_data=keep_data)
        return

    if operation == "delete":
        drop_table(table=table)


def create_table(table, confirmation=True) -> None:
    answer = exe.execute_query(sql=TABLE_CONFIG[table]['create_sql'], header=False, capture=True)
    
    output = f"TABLE '{TABLE_CONFIG[table]['table_name']}'"
    
    if answer.stderr and "already exists" in answer.stderr.strip():
        ff.print_colored(text=f"{output} NOT CREATED - ALREADY EXISTS.\n", color="YELLOW")
        return
    
    ff.print_colored(text=f"{output} CREATED.\n", color="GREEN", really_print=confirmation)

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

def drop_table(table, confirmation=True) -> None:
    answer = exe.execute_query(sql=TABLE_CONFIG[table]['drop_sql'], header=False, capture=True)
    
    output = f"TABLE '{TABLE_CONFIG[table]['table_name']}'"
    
    if answer.stderr and "does not exist" in answer.stderr.strip():
        ff.print_colored(text=f"{output} NOT DELETED - DOESN'T EXIST.\n", color="YELLOW")
        return
    
    ff.print_colored(text=f"{output} DELETED.\n", color="GREEN", really_print=confirmation)
