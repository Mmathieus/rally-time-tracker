import config as cnfg

import utils.formatter as ff
import utils.inputter as ii
import utils.validator as vv

import database.tools.executor as exe
import database.tools.state as stt


RECORDS_FROM_OLDEST = cnfg.config['command']['select']['records_order']['from_oldest']
RECORDS_FROM_NEWEST = cnfg.config['command']['select']['records_order']['from_newest']

RECORDS_ORDER_OPTIONS = RECORDS_FROM_OLDEST + RECORDS_FROM_NEWEST

DEFAULT_ORDER = " ORDER BY rally, time, stage;"


def select_manager(search_term=None, time_order=None, order_limit=None) -> None:
    # Check if DB/TABLE exists (primary)
    if not stt.check_db_exists_state(
        table=cnfg.PRIMARY_TB_NAME, info_message=ff.colorize(text="RECORD(S) NOT RETRIEVED. {rest}\n", color="YELLOW")
    )[0]:
        return
    
    # Something directly after command
    if search_term:
        select_exec(search_term=ff.to_pascal_kebab_case(term=search_term), time_order=time_order, order_limit=order_limit)
        return
    
    # Selecting RALLY + formatting
    rally = ff.to_pascal_kebab_case(term=ii.get_user_input(prompt="RALLY", autocomplete_options=list(cnfg.WRC_RALLIES.keys())))

    stage_options = cnfg.get_stages(rally=rally)
    # Selecting STAGE + formatting
    stage = ff.to_pascal_kebab_case(term=ii.get_user_input(prompt="STAGE", autocomplete_options=stage_options))

    select_exec(rally=rally, stage=stage)

def select_exec(rally=None, stage=None, search_term=None, time_order=None, order_limit=None) -> None:
    SELECT_QUERY = "SELECT id, rally, stage, car, TO_CHAR(time, 'MI:SS:MS') AS time, created_at FROM timings"

    # 'select' typed
    if not search_term:
        conditions = []
        if rally: conditions.append(f"rally = '{rally}'")
        if stage: conditions.append(f"stage = '{stage}'")

        if conditions != []:
            SELECT_QUERY += f" WHERE {' AND '.join(conditions)}"

        SELECT_QUERY += DEFAULT_ORDER
    
    # 'select [search_term]' typed
    else:
        # Normal search_term -> not EVERYTHING_ALIAS
        if not search_term == ff.to_pascal_kebab_case(term=cnfg.EVERYTHING_ALIAS):
            SELECT_QUERY += f" WHERE rally = '{search_term}' OR stage = '{search_term}'{DEFAULT_ORDER}"

        # Search_term is EVERYTHING_ALIAS
        else:
            # Check ORDERING term
            if time_order:
                validated, validation_message = vv.validate_choice(choice=time_order.lower(), valid_options=RECORDS_ORDER_OPTIONS, choice_name="ORDER")
                if not validated:
                    ff.print_colored(text=f"{validation_message}\n", color="RED")
                    return
            
            # Check ORDERING LIMIT number
            if order_limit and not order_limit.isdigit():
                print(
                    f"{ff.colorize(text=f"INVALID LIMIT '{order_limit}'.", color="RED")} "
                    f"{ff.colorize(text=" WHOLE POSITIVE NUMBER EXPECTED.", color="YELLOW")}\n"
                )
                return
            
            limit_value = order_limit if order_limit else "ALL"

            # Complete query with correct ORDER clause
            if not time_order:
                SELECT_QUERY += DEFAULT_ORDER
            else:
                order_direction = "ASC" if time_order in RECORDS_FROM_OLDEST else "DESC"
                SELECT_QUERY += f" ORDER BY created_at {order_direction} LIMIT {limit_value};"

    print()
    exe.execute_query(sql=SELECT_QUERY)
