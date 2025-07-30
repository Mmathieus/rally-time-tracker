import utils.formatter as ff
import utils.inputter as ii
import utils.other as oo

import database.tools.executor as exe


HISTORY_QUERY_ALL = "SELECT id, rally, stage, car, TO_CHAR(time, 'MI:SS:MS') AS time, created_at FROM timings_history ORDER BY rally, stage, time DESC;"
HISTORY_QUERY_SPECIFIC = """
    SELECT
        id rally, stage, car, TO_CHAR(time, 'MI:SS:MS') AS time,
        TO_CHAR(imprvmnt, '"-"MI:SS:MS') AS gain,
        TO_CHAR(SUM(imprvmnt) OVER (PARTITION BY stage ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), '"-"MI:SS:MS') AS total_gain,
        created_at
    FROM (
        SELECT
            id, rally, stage, car, time,
            LAG(time) OVER (PARTITION BY stage ORDER BY id) - time AS imprvmnt,
            created_at FROM timings_history
        WHERE stage = '{stage}') AS subquery
    ORDER BY id;
"""


def history_manger(stage=None) -> None:
    if not _exists_timings_history():
        return
    
    if stage:
        _history_exec(stage=stage)
        return
    
    stage = ii.get_user_input(prompt="STAGE")

    _history_exec(stage=stage)

def _history_exec(stage) -> None:
    if not _exists_timings_history():
        return
    
    stage = ff.upper_casing(term=stage)
    
    query = HISTORY_QUERY_SPECIFIC.format(stage=stage)
    
    if stage in ('.', ''):
        query = HISTORY_QUERY_ALL
    
    print()
    exe.execute_query(sql=query)


def _exists_timings_history() -> bool:
    all_ok, info_message = oo.get_db_exists_state(table="timings_history", include_table_name=True)
    if not all_ok:
        ff.print_colored(text=f"RECORD(S) NOT RETRIEVED. {info_message}\n", color="YELLOW")
        return False
    return True
