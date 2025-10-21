import config as cnfg
import database.tools.executor as exe


def capture_current_db_state() -> None:
    # Setting aliases for convenience
    DATABASE = cnfg.db_state['database']
    TIMINGS = cnfg.db_state['timings']
    TIMINGS_HISTORY = cnfg.db_state['timings_history']

    DATABASE['exists'] = _database_exists()

    # DATABASE not present -> nothing (else) we can do
    if not DATABASE['exists']:
        # Override everything to 'None' (functional reason)
        TIMINGS.update({key: None for key in TIMINGS})
        TIMINGS_HISTORY.update({key: None for key in TIMINGS_HISTORY})
        # Overriding 'DATABASE['size']' is not neccesary
        return
    
    DATABASE['size'] = _get_database_info()

    TIMINGS['exists'] = _table_exists(table=cnfg.PRIMARY_TB_NAME)

    # TIMINGS info only if EXISTS
    if TIMINGS['exists']:
        TIMINGS['size'], TIMINGS['data_size'], TIMINGS['records'] = _get_table_info(table=cnfg.PRIMARY_TB_NAME)
    
    TIMINGS_HISTORY['exists'] = _table_exists(table=cnfg.HISTORY_TB_NAME)

    # TIMINGS_HISTORY info only if EXISTS
    if TIMINGS_HISTORY['exists']:
        TIMINGS_HISTORY['size'], TIMINGS_HISTORY['data_size'], TIMINGS_HISTORY['records'] = _get_table_info(table=cnfg.HISTORY_TB_NAME)


def _database_exists() -> bool:
    result = exe.execute_query(sql=f"SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname = '{cnfg.DB_NAME}');", header=False, capture=True, postgres_db=True)
    if result.stdout.strip() == 't':
        return True
    return False
    
def _table_exists(table) -> bool:
    result = exe.execute_query(sql=f"SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = '{table}');", header=False, capture=True)
    if result.stdout.strip() == 't':
        return True
    return False

def _get_database_info() -> int:
    result = exe.execute_query(sql=f"SELECT pg_database_size('{cnfg.DB_NAME}');", header=False, capture=True, postgres_db=True)
    return int(result.stdout.strip())

def _get_table_info(table) -> tuple[int, int, int]:
    TABLE_STATS_QUERY = f"""
        SELECT 
            pg_total_relation_size('{table}'),
            pg_relation_size('{table}'),
            (SELECT COUNT(*) FROM {table});
    """

    result = exe.execute_query(sql=TABLE_STATS_QUERY, header=False, capture=True)
    info = result.stdout.strip().split('|')
    return tuple(int(x.strip()) for x in info)
