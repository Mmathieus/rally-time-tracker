import config as cnfg

import utils.formatter as ff
import utils.other as oo

import database.tools.executor as exe

SEQUENCE_QUERY = """
    SELECT setval(
        pg_get_serial_sequence('timings', 'id'), 
        (SELECT GREATEST(
            COALESCE(MAX(timings.id), 0),
            COALESCE(MAX(timings_history.id), 0)
        ) FROM timings, timings_history)
    ) + 1 AS next_id;
"""

# Obidve tabuľky musia existovať
# +
# NE(musia) obsahovať záznamy (aspoň 1)

def _is_update_possible(from_table) -> bool:
    if from_table == "timings":
        if not cnfg.db_state['timings_history']['exists']:
            return False
        return True
    
    if from_table == "timings_history":
        if not cnfg.db_state['timings']['exists']:
            return False
        return True



def update_sequence(calling_from, print_confirmation=False) -> None:
    if not _is_update_possible(from_table=calling_from):
        return

    # exists, info_message = oo.get_db_exists_state(table="timings", include_table_name=True)
    # if not exists:
    #     ff.print_colored(text=f"ID SEQUENCE NOT REFRESHED. {info_message}\n", color="YELLOW")
    #     return
    
    exe.execute_query(sql=SEQUENCE_QUERY, capture=False) # not print_confirmation
