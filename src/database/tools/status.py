import config as cnfg

import database.tools.executor as exe

# import copy


# DB_STATE_TEMPLATE = {
#     'database': { 
#         'exists': None,
#         'size': None
#     },
#     'timings': {
#         'exists': None,
#         'size': None,
#         'data_size': None,
#         'records': None
#     },
#     'timings_history': {
#         'exists': None,
#         'size': None,
#         'data_size': None,
#         'records': None
#     }
# }

DB_NAME = cnfg.config['db_connection']['database']
TABLES = ("timings", "timings_history")


def get_current_db_state() -> None:
    # cnfg.db_state = copy.deepcopy(DB_STATE_TEMPLATE)

    DATABASE = cnfg.db_state['database']
    TIMINGS = cnfg.db_state['timings']
    TIMINGS_HISTORY = cnfg.db_state['timings_history']

    DATABASE['exists'] = _database_exists()

    # DATABASE not present -> nothing (else) we can do
    if not DATABASE['exists']:
        return
    
    DATABASE['size'] = _get_database_info()

    TIMINGS['exists'] = _table_exists(table="timings")

    # TIMINGS info only if EXISTS
    if TIMINGS['exists']:
        TIMINGS['size'], TIMINGS['data_size'], TIMINGS['records'] = _get_table_info(table="timings")
    
    TIMINGS_HISTORY['exists'] = _table_exists(table="timings_history")

    # TIMINGS_HISTORY info only if EXISTS
    if TIMINGS_HISTORY['exists']:
        TIMINGS_HISTORY['size'], TIMINGS_HISTORY['data_size'], TIMINGS_HISTORY['records'] = _get_table_info(table="timings_history")


def _database_exists() -> bool:
    result = exe.execute_query(sql=f"SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}');", header=False, capture=True, postgres_db=True)
    if result.stdout.strip() == 't':
        return True
    return False
    
def _table_exists(table) -> bool:
    result = exe.execute_query(sql=f"SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = '{table}');", header=False, capture=True)
    if result.stdout.strip() == 't':
        return True
    return False

def _get_database_info() -> int:
    result = exe.execute_query(sql=f"SELECT pg_database_size('{DB_NAME}');", header=False, capture=True, postgres_db=True)
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
