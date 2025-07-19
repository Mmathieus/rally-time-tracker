from utils import formatter as ff, inputter as ii
from database.others import executor as exe


def _select_manager(search_term=None) -> None:
    if search_term:
        _select_exec(fuzzy_search=True, search_term=ff.upper_casing(term=search_term))
        return
    
    rally = ii.get_user_input(prompt="RALLY")
    stage = ii.get_user_input(prompt="STAGE")

    _select_exec(rally=ff.upper_casing(term=rally), stage=ff.upper_casing(term=stage))


def _select_exec(rally=None, stage=None, fuzzy_search=False, search_term=None) -> None:
    SELECT_QUERY = "SELECT rally, stage, car, TO_CHAR(time, 'MI:SS:MS') AS time, created_at FROM timings"
    
    if fuzzy_search:
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
