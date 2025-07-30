import utils.formatter as ff
import utils.inputter as ii
import utils.other as oo

import database.tools.executor as exe


def select_manager(search_term=None) -> None:
    if not _exists_timings():
        return
    
    if search_term:
        select_exec(fuzzy_search=True, search_term=ff.upper_casing(term=search_term))
        return
    
    rally = ii.get_user_input(prompt="RALLY")
    stage = ii.get_user_input(prompt="STAGE")

    select_exec(rally=ff.upper_casing(term=rally), stage=ff.upper_casing(term=stage))

def select_exec(rally=None, stage=None, fuzzy_search=False, search_term=None) -> None:
    if not _exists_timings():
        return

    SELECT_QUERY = "SELECT id, rally, stage, car, TO_CHAR(time, 'MI:SS:MS') AS time, created_at FROM timings"
    
    if fuzzy_search:
        if search_term != '.':
            SELECT_QUERY += f" WHERE rally = '{search_term}' OR stage = '{search_term}'"
    else:
        conditions = []
        if rally: conditions.append(f"rally = '{rally}'")
        if stage: conditions.append(f"stage = '{stage}'")

        if conditions != []:
            SELECT_QUERY += f" WHERE {' AND '.join(conditions)}"
        
    SELECT_QUERY += " ORDER BY rally, time ASC, stage;"
    
    print()
    exe.execute_query(sql=SELECT_QUERY)


def _exists_timings() -> bool:
    all_ok, info_message = oo.get_db_exists_state(table="timings", include_table_name=True)
    if not all_ok:
        ff.print_colored(text=f"RECORD(S) NOT RETRIEVED. {info_message}\n", color="YELLOW")
        return False
    return True
