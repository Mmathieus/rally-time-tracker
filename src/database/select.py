import config as cnfg

import utils.formatter as ff
import utils.inputter as ii
import utils.other as oo
import utils.validator as vv

import database.tools.executor as exe


EVERYTHING_ALIAS = cnfg.config['everything_reference']

DEFAULT_ORDER = " ORDER BY rally, time ASC, stage;"

OLDEST_TIME_ORDERING_OPTIONS = cnfg.config['operations']['select']['time_ordering']['oldest']
NEWEST_TIME_ORDERING_OPTIONS = cnfg.config['operations']['select']['time_ordering']['newest']

TIME_ORDERING_OPTIONS = OLDEST_TIME_ORDERING_OPTIONS + NEWEST_TIME_ORDERING_OPTIONS


def select_manager(search_term=None, time_order=None, order_limit=None) -> None:
    if not _exists_timings():
        return
    
    if search_term:
        select_exec(fuzzy_search=True, search_term=ff.upper_casing(term=search_term), time_order=time_order, order_limit=order_limit)
        return
    
    rally = ii.get_user_input(prompt="RALLY")
    stage = ii.get_user_input(prompt="STAGE")

    select_exec(rally=ff.upper_casing(term=rally), stage=ff.upper_casing(term=stage))

def select_exec(rally=None, stage=None, fuzzy_search=False, search_term=None, time_order=None, order_limit=None) -> None:
    SELECT_QUERY = "SELECT id, rally, stage, car, TO_CHAR(time, 'MI:SS:MS') AS time, created_at FROM timings"

    if not fuzzy_search:
        conditions = []
        if rally: conditions.append(f"rally = '{rally}'")
        if stage: conditions.append(f"stage = '{stage}'")

        if conditions != []:
            SELECT_QUERY += f" WHERE {' AND '.join(conditions)}"

        SELECT_QUERY += DEFAULT_ORDER
    
    else:
        # It's '.' / 'all' / ...
        if search_term == ff.upper_casing(term=EVERYTHING_ALIAS):
            if time_order and not vv.validate_choice(choice=time_order.lower(), valid_options=TIME_ORDERING_OPTIONS):
                return
            
            if order_limit and not order_limit.isdigit():
                ff.print_colored(text="INVALID LIMIT. WHOLE POSITIVE NUMBER EXPECTED.\n", color="YELLOW")
                return
            
            limit_value = order_limit if order_limit else "ALL"

            if not time_order:
                SELECT_QUERY += DEFAULT_ORDER
            elif time_order in OLDEST_TIME_ORDERING_OPTIONS:
                SELECT_QUERY += f" ORDER BY created_at ASC LIMIT {limit_value};"
            else:
                SELECT_QUERY += f" ORDER BY created_at DESC LIMIT {limit_value};"
        # Normal search_term -> It's NOT '.' / 'all' / ...
        else:
            SELECT_QUERY += f" WHERE rally = '{search_term}' OR stage = '{search_term}'{DEFAULT_ORDER}"

    print()
    exe.execute_query(sql=SELECT_QUERY)


def _exists_timings() -> bool:
    all_ok, info_message = oo.get_db_exists_state(table="timings", include_table_name=True)
    if not all_ok:
        ff.print_colored(text=f"RECORD(S) NOT RETRIEVED. {info_message}\n", color="YELLOW")
        return False
    return True
