import config as cnfg

import database.tools.executor as exe

import utils.formatter as ff


# Used when 'command 'all'' is called to verify DB/TABLES existence based on given arguments
def verify_db_exists_state(both_required=False, must_exist=True, include_table_name=True, bad_info_message="") -> bool:
    
    # Check primary table
    primary_ok, primary_message = _get_db_exists_state(table=cnfg.PRIMARY_TB_NAME, must_exists=must_exist, include_table_name=include_table_name)
    # Primary table not ok
    if not primary_ok:
        # Something wrong with database -> done here
        if "DATABASE" in primary_message:
            print(f"{bad_info_message.format(rest=primary_message)}")
            return False
    
    # Check history table
    history_ok, history_message = _get_db_exists_state(table=cnfg.HISTORY_TB_NAME, must_exists=must_exist, include_table_name=include_table_name)
    

    # Determine tables count message
    tables_count_message = "NEITHER TABLE EXISTS." if must_exist else "BOTH TABLES EXIST."


    # At least 1 is required but both are not OK
    if not both_required and (not primary_ok and not history_ok):
        print(bad_info_message.format(rest=tables_count_message))
        return False


    # Both are required and both aren't OK
    if both_required and (not primary_ok and not history_ok):
        print(bad_info_message.format(rest=tables_count_message))
        return False
    
    # Both are required and only primary is OK
    if both_required and (primary_ok and not history_ok):
        print(bad_info_message.format(rest=history_message))
        return False

    # Both are required and only history is OK
    if both_required and (not primary_ok and history_ok):
        print(bad_info_message.format(rest=primary_message))
        return False
    
    return True

# Used in specific files to check if DB/TABLES are present | Gets result from Core function and determines output based on given arguments
def check_db_exists_state(table=None, must_exists=True, include_table_name=True, info_message="", info_message_decision="print") -> tuple[bool, str]:
    all_ok, existence_message = _get_db_exists_state(table=table, must_exists=must_exists, include_table_name=include_table_name)
    
    returning_string = info_message.format(rest=existence_message)

    if all_ok:
        return True, returning_string
    
    if info_message_decision == "return":
        return False, returning_string
    
    if info_message_decision == "print":
        print(returning_string)
        return False, returning_string
    
    ff.print_colored(text=f"SYSTEM ERROR: wrong argument 'info_message_decision': {info_message_decision}\n", color="RED")
    return False, "ERROR"


# Core function -> returns if its 'ALL OK' and 'info message' 
def _get_db_exists_state(table=None, must_exists=True, include_table_name=True) -> tuple[bool, str]:
    db_exists = cnfg.db_state['database']['exists']
    
    # Checking only Database existence
    if not table:
        # Database must exists AND it does
        if must_exists and db_exists:
            return True, "DATABASE ALREADY EXISTS."
        # Database must exists BUT it doesn't
        elif must_exists and not db_exists:
            return False, "DATABASE DOESN'T EXIST."
        # Database mustn't exists BUT it does
        elif not must_exists and db_exists:
            return False, "DATABASE ALREADY EXISTS."
        # Database mustn't exists AND it doesn't
        elif not must_exists and not db_exists:
            return True, "DATABASE DOESN'T EXIST."
    
    # Checking Table -> Database must exists in every circumstances
    if not db_exists:
        return False, "DATABASE DOESN'T EXIST."
    
    table_exists = cnfg.db_state[table]['exists']
    table_name = f"'{table}' " if include_table_name else ""

    # Table must exists AND it does
    if must_exists and table_exists:
        return True, f"TABLE {table_name}ALREADY EXISTS."
    # Table must exists BUT it doesn't
    elif must_exists and not table_exists:
        return False, f"TABLE {table_name}DOESN'T EXIST."
    # Table mustn't exists BUT it does
    elif not must_exists and table_exists:
        return False, f"TABLE {table_name}ALREADY EXISTS."
    # Table mustn't exists AND it doesn't
    elif not must_exists and not table_exists:
        return True, f"TABLE {table_name}DOESN'T EXIST."


# -------------------------------------

# Reducing state calls from 6 to 2, for time and efficiency

DATABASE_STATE_QUERY = """
    SELECT
        EXISTS(SELECT 1 FROM pg_database WHERE datname = '{database}'),
        (SELECT pg_database_size(oid) FROM pg_database WHERE datname = '{database}');
"""

# 'to_regclass' returns NULL instead of failing on a missing table
# -> both tables can be asked about at once 'query_to_xml' runs the COUNT through a string, so a missing table doesn't break the whole query either
TABLES_STATE_QUERY = """
    SELECT
        tb.name,
        to_regclass(tb.name) IS NOT NULL,
        COALESCE(pg_total_relation_size(to_regclass(tb.name)), 0),
        COALESCE(pg_relation_size(to_regclass(tb.name)), 0),
        CASE WHEN to_regclass(tb.name) IS NOT NULL
             THEN (xpath('/row/c/text()', query_to_xml('SELECT COUNT(*) AS c FROM ' || quote_ident(tb.name), false, true, '')))[1]::text::bigint
        END
    FROM (VALUES ('{primary_table}'), ('{history_table}')) AS tb(name);
"""


def capture_current_db_state() -> None:
    # Setting aliases for convenience
    DATABASE = cnfg.db_state['database']
    TIMINGS = cnfg.db_state['timings']
    TIMINGS_HISTORY = cnfg.db_state['timings_history']

    DATABASE['exists'], DATABASE['size'] = _get_database_state()

    # DATABASE not present -> nothing (else) we can do
    if not DATABASE['exists']:
        # Override everything to 'None' (functional reason)
        TIMINGS.update({key: None for key in TIMINGS})
        TIMINGS_HISTORY.update({key: None for key in TIMINGS_HISTORY})
        # Overriding 'DATABASE['size']' is not necessary
        return

    TABLES_STATE = _get_tables_state()

    TIMINGS.update(TABLES_STATE[cnfg.PRIMARY_TB_NAME])
    TIMINGS_HISTORY.update(TABLES_STATE[cnfg.HISTORY_TB_NAME])


# 1 'psql' call -> DATABASE existence + size
def _get_database_state() -> tuple[bool, int | None]:
    result = exe.execute_query(sql=DATABASE_STATE_QUERY.format(database=cnfg.DB_NAME), header=False, capture=True, postgres_db=True)

    exists, size = (value.strip() for value in result.stdout.split('|'))

    # DATABASE not present -> 'size' comes back empty
    return exists == 't', int(size) if size else None

# 1 'psql' call -> TABLES existence + size + data_size + records
def _get_tables_state() -> dict[str, dict]:
    result = exe.execute_query(
        sql=TABLES_STATE_QUERY.format(primary_table=cnfg.PRIMARY_TB_NAME, history_table=cnfg.HISTORY_TB_NAME),
        header=False, capture=True
    )

    tables_state = {}

    # 1 row per table
    for row in result.stdout.strip().splitlines():
        name, exists, size, data_size, records = (value.strip() for value in row.split('|'))

        # TABLE not present -> nothing (else) to report
        if exists != 't':
            tables_state[name] = {'exists': False, 'size': None, 'data_size': None, 'records': None}
            continue

        tables_state[name] = {'exists': True, 'size': int(size), 'data_size': int(data_size), 'records': int(records)}

    return tables_state
