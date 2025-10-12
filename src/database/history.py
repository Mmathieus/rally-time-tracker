import config as cnfg

import utils.formatter as ff
import utils.inputter as ii

import database.tools.executor as exe
import database.tools.other as othr


HISTORY_QUERY_ALL = """
    SELECT id, rally, stage, car, TO_CHAR(time, 'MI:SS:MS') AS time, created_at
    FROM timings_history
    ORDER BY rally, stage, time DESC;
"""

HISTORY_QUERY_SPECIFIC = """
    SELECT
        id, rally, stage, car, TO_CHAR(time, 'MI:SS:MS') AS time,
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


def history_manager(stage=None) -> None:
    # Check if DB/TABLE exists (history)
    all_ok, info_message = othr.get_db_exists_state(table=cnfg.HISTORY_TB_NAME, include_table_name=True)
    if not all_ok:
        ff.print_colored(text=f"RECORD(S) NOT RETRIEVED. {info_message}\n", color="YELLOW")
        return
    
    if not stage:
        stage_options = cnfg.get_stages()
        stage = ii.get_user_input(prompt="STAGE", autocomplete_options=stage_options)

    _history_exec(stage=ff.to_pascal_kebab_case(term=stage))

def _history_exec(stage) -> None:
    query = HISTORY_QUERY_SPECIFIC.format(stage=stage)
    
    if stage == ff.to_pascal_kebab_case(term=cnfg.EVERYTHING_ALIAS):
        query = HISTORY_QUERY_ALL
    
    print()
    exe.execute_query(sql=query)
