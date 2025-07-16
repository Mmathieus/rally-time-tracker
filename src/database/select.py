from utils import formatter as ff
from database import executor


def _select_manager(search_term=None) -> None:
    if search_term:
        _select_exec(loose_matching=True, searching_term=ff.upper_casing(term=search_term))
        return
    
    rally = input("🗺️ RALLY: ").strip()
    stage = input("🚥 STAGE: ").strip()

    _select_exec(rally=ff.upper_casing(term=rally), stage=ff.upper_casing(term=stage))

def _select_exec(rally=None, stage=None, fuzzy_search=False, search_term=None) -> None:
    SELECT_QUERY = "SELECT rally, stage, car, TO_CHAR(time, 'MI:SS:MS') AS time, created_at FROM timings"
    ENDING = " ORDER BY rally, stage, time DESC;"
    
    if fuzzy_search:
        SELECT_QUERY += f" WHERE rally = '{search_term}' OR stage = '{search_term}'" + ENDING
    else:
        conditions = []
        if rally: conditions.append(f"rally = '{rally}'")
        if stage: conditions.append(f"stage = '{stage}'")

        if conditions != []:
            SELECT_QUERY += f" WHERE {' AND '.join(conditions)}" + ENDING
    
    print()
    executor.execute_query(sql=SELECT_QUERY)
