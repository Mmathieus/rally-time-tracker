import config as cnfg

import utils.formatter as ff
import utils.inputter as ii
import utils.other as oo

import database.select as slct
import database.tools.executor as exe

import re


DEFAULT_CAR = cnfg.config['command']['insert']['default_car']
DEFAULT_CAR_CODE = cnfg.config['command']['insert']['default_car_code']

CONFIRMATION_SELECT_AFTER_INSERT = cnfg.config['command']['insert']['confirmation_select_after_insert']

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
        INPUT_ALIGN_WIDTH = 8

        # RALLY
        rally = ii.get_user_input(prompt="RALLY", autocomplete_options=cnfg.get_rallies(), align_width=INPUT_ALIGN_WIDTH)
        if not rally:
            print(); return
        
        # STAGE
        stage = ii.get_user_input(prompt="STAGE", autocomplete_options=cnfg.get_stages(rally=ff.to_pascal_kebab_case(term=rally)), align_width=INPUT_ALIGN_WIDTH)
        if not stage:
            print(); return
        
        # CAR
        car = ii.get_user_input(prompt="CAR", autocomplete_options=cnfg.WRC_CARS, align_width=INPUT_ALIGN_WIDTH)
        if not car:
            print(); return
        
        #TIME
        time = ii.get_user_input(prompt="TIME", align_width=INPUT_ALIGN_WIDTH)
        if not time:
            print(); return
    
    # TIME validation
    if not _validate_time_format(time=time):
        print(
            f"{ff.colorize(text=f"INVALID TIME FORMAT.", color="RED")} "
            f"{ff.colorize(text="EXPECTED FORMAT: '(M)M:SS:mmm'. MAX - 59:59.999.", color="YELLOW")}\n"
        )
        return

    # Check if DB/TABLE exists (primary)
    all_ok, info_message = oo.get_db_exists_state(table=cnfg.PRIMARY_TB_NAME, include_table_name=True)
    if not all_ok:
        ff.print_colored(text=f"INSERT ABORTED. {info_message}\n", color="YELLOW")
        return
    
    rally, stage = map(ff.to_pascal_kebab_case, (rally, stage))
    # Replace last ':' for '.'
    time = re.sub(r':([^:]*)$', r'.\1', time)

    record_exists, record_id, improvement = _compare_with_existing_record(stage=stage, time=time)

    if record_exists:
        # There's improvement or exactly the same time
        if improvement and record_id:
            # 'else' statement from this 'if' is IMPROVED record. -> Letting it/him go for now...
            if re.fullmatch(r'[0:]*', improvement):
                ff.print_colored(text=f"INSERT ABORTED. STAGE '{stage}' NOT IMPROVED. EXACTLY THE SAME TIME.", color="YELLOW")
                print(f"+- {improvement}\n")
                return
        else:
            print(
                f"{ff.colorize(text=f"INSERT ABORTED. STAGE '{stage}' NOT IMPROVED.\n", color="YELLOW")}"
                f"{ff.colorize(text=f"+ {improvement}\n", color="RED")}"
            )
            return
    
    # Check if DB/TABLE exists (timings_history)
    all_ok, info_message = oo.get_db_exists_state(table=cnfg.HISTORY_TB_NAME, include_table_name=True)
    if not all_ok:
        ff.print_colored(text=f"INSERT ABORTED. {info_message}\n", color="YELLOW")
        return
    
    car = DEFAULT_CAR if car == DEFAULT_CAR_CODE else car

    _insert_exec(rally=rally, stage=stage, car=car, time=time, gain=improvement, old_record_id=record_id)

def _insert_exec(rally, stage, car, time, gain, old_record_id) -> None:
    delete_query = f"DELETE FROM timings WHERE id = {old_record_id};" if gain else ""

    exe.execute_query(sql=INSERT_QUERY.format(rally=rally, stage=stage, car=car, time=time, delete_query=delete_query), header=False, capture=True)

    print(
        f"{ff.colorize(text=f"NEW RECORD INSERTED INTO '{cnfg.PRIMARY_TB_NAME}' TABLE.\n", color="GREEN")}"
        f"{ff.colorize(text=f"NEW RECORD INSERTED INTO '{cnfg.HISTORY_TB_NAME}' TABLE.", color="GREEN")}"
    )

    if gain:
        print(
            f"{ff.colorize(text=f"OLD RECORD DELETED FROM '{cnfg.PRIMARY_TB_NAME}' TABLE.\n", color="GREEN")}"
            f"{ff.colorize(text=f"- {gain}", color="MAGENTA")}"
        )

    print()
    if CONFIRMATION_SELECT_AFTER_INSERT:
        slct.select_exec(search_term=stage)


def _validate_time_format(time) -> bool:
    # (M)M:SS:mmm | MAX - 59:59:999
    time_pattern = r'^([0-9]|[0-5][0-9]):(0[0-9]|[1-5][0-9]):\d{3}$'
    if not re.match(time_pattern, time):
        return False
    return True

def _compare_with_existing_record(stage, time) -> tuple[bool, int | None, str | None]:
    result = exe.execute_query(sql=COMPARING_QUERY.format(time=time, stage=stage), header=False, capture=True)
    data = result.stdout.strip()

    # RETURN VALUES = (record_exists, record_id, improvement)

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
