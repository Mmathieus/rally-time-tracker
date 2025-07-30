import config as cnfg

import utils.formatter as ff
import utils.inputter as ii
import utils.other as oo

import database.select as slct
import database.tools.executor as exe

import re


DEFAULT_CAR = cnfg.config['operations']['insert']['default_car']
DEFAULT_CAR_CODE = cnfg.config['operations']['insert']['default_car_code']

CONFIRMATION_SELECT_AFTER_INSERT = cnfg.config['operations']['insert']['confirm_insert']

COMPARING_QUERY = """
    SELECT ROW(
        COALESCE(id, NULL),
        COALESCE(TO_CHAR(time - '{time}'::INTERVAL, '"-"MI:SS:MS'), NULL)
        ) AS id_improvement
    FROM timings
    WHERE stage = '{stage}';
"""

INSERT_QUERY = """
    BEGIN;
        INSERT INTO timings(rally, stage, car, time) VALUES ('{rally}', '{stage}', '{car}', '{time}'::INTERVAL);
        INSERT INTO timings_history SELECT * FROM timings WHERE stage = '{stage}' ORDER BY id DESC LIMIT 1;
        {delete_query}
    COMMIT;
"""


def insert_manager(rally=None, stage=None, car=None, time=None) -> None:
    if not rally:
        inputs = []
        for prompt in ["RALLY", "STAGE", "CAR", "TIME"]:
            value = ii.get_user_input(prompt=prompt)
            if not value:
                print()
                return
            inputs.append(value)
    
        rally, stage, car, time = inputs
    
    if not _validate_time_format(time=time):
        ff.print_colored(text="INVALID TIME FORMAT. EXPECTED FORMAT: '(M)M:SS:mmm'. MAX - 59:59.999.\n", color="RED")
        return
    
    all_ok, info_message = oo.get_db_exists_state(table="timings", include_table_name=True)
    if not all_ok:
        ff.print_colored(text=f"INSERT ABORTED. {info_message}\n", color="YELLOW")
        return
    
    rally, stage = map(ff.upper_casing, (rally, stage))
    time = re.sub(r':([^:]*)$', r'.\1', time)

    record_exists, record_id, improvement = _compare_with_existing_record(stage=stage, time=time)

    if record_exists:
        if improvement and record_id:
            # 'else' statement from this 'if' is IMPROVED record. -> Letting it/him go.
            if re.fullmatch(r'[0:]*', improvement):
                ff.print_colored(text=f"INSERT ABORTED. STAGE '{stage}' NOT IMPROVED. EXACTLY THE SAME TIME.", color="YELLOW")
                print(f"+- {improvement}\n")
                return
        else:
            ff.print_colored(text=f"INSERT ABORTED. STAGE '{stage}' NOT IMPROVED.", color="YELLOW")
            ff.print_colored(text=f"+ {improvement}\n", color="RED")
            return
        
    all_ok, info_message = oo.get_db_exists_state(table="timings_history", include_table_name=True)
    if not all_ok:
        ff.print_colored(text=f"INSERT ABORTED. {info_message}\n", color="YELLOW")
        return
    
    car = DEFAULT_CAR if car == DEFAULT_CAR_CODE else car

    _insert_exec(rally=rally, stage=stage, car=car, time=time, gain=improvement, old_record_id=record_id)

def _insert_exec(rally, stage, car, time, gain, old_record_id) -> None:
    delete_query = f"DELETE FROM timings WHERE id = {old_record_id};" if gain else ""

    exe.execute_query(sql=INSERT_QUERY.format(rally=rally, stage=stage, car=car, time=time, delete_query=delete_query), header=False, capture=True)

    ff.print_colored(text="NEW RECORD INSERTED INTO 'timings' TABLE.", color="GREEN")
    ff.print_colored(text="NEW RECORD INSERTED INTO 'timings_history' TABLE.", color="GREEN")

    if gain:
        ff.print_colored(text="OLD RECORD DELETED FROM 'timings' TABLE.", color="GREEN")
        ff.print_colored(text=f"- {gain}", color="MAGENTA")

    print()
    if CONFIRMATION_SELECT_AFTER_INSERT:
        slct.select_exec(fuzzy_search=True, search_term=stage)


def _validate_time_format(time) -> bool:
    time_pattern = r'^([0-9]|[0-5][0-9]):(0[0-9]|[1-5][0-9]):\d{3}$'
    if not re.match(time_pattern, time):
        return False
    return True

def _compare_with_existing_record(stage, time) -> tuple[bool, int | None, str | None]:
    result = exe.execute_query(sql=COMPARING_QUERY.format(time=time, stage=stage), header=False, capture=True)
    data = result.stdout.strip()

    # Completely new STAGE.
    if not data:
        return False, None, None
    
    is_improved = data.count('-')

    data = re.sub(r'[-()]', '', data)

    db_id, db_time = data.split(',')
    
    # STAGE exists but not improved
    if is_improved > 1:
        return True, None, db_time
    
    # STAGE exists and improved
    return True, int(db_id), db_time
