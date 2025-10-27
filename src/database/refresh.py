import config as cnfg

import utils.formatter as ff
import utils.validator as vv

import database.create__drop as cd
import database.tools.executor as exe
import database.tools.sequence as sqnc
import database.tools.state as stt
import database.tools.other as othr

import os


KEEP_DATA_OPTIONS = cnfg.config['command']['refresh']['data_handling']['keep']
LOSE_DATA_OPTIONS = cnfg.config['command']['refresh']['data_handling']['lose']
DATA_OPTIONS = KEEP_DATA_OPTIONS + LOSE_DATA_OPTIONS


def refresh_manager(target, keep_data=None) -> None:
    # Refresh both tables
    if target == cnfg.EVERYTHING_ALIAS:
        
        # Determine 'keep_data' value
        keep_data = _determine_keep_data(keep_data=keep_data)  

        print()
        refresh_manager(target=cnfg.PRIMARY_TB_ALIAS, keep_data=keep_data)
        refresh_manager(target=cnfg.HISTORY_TB_ALIAS, keep_data=keep_data)
        return


    # Check table name
    if target not in cnfg.BOTH_TABLES:
        ff.print_colored(text=f"INVALID TABLE NAME '{target}'.\n", color="RED")
        return
    
    # Check if DB/TABLE exists
    if not stt.check_db_exists_state(
        table=cnfg.get_tb_name(table=target),
        info_message=ff.colorize(text=f"TABLE '{cnfg.get_tb_name(table=target)}' NOT REFRESHED. {{rest}} \n", color="YELLOW")
    )[0]:
        return
    
    # Determine 'keep_data' value
    keep_data = _determine_keep_data(keep_data=keep_data)
    if not keep_data:
        return
    
    _refresh_exec(table=target, keep_data=keep_data)

def _refresh_exec(table, keep_data) -> None:
    TABLE_NAME = cnfg.get_tb_name(table=table)

    if keep_data in KEEP_DATA_OPTIONS:
        transaction = f"""
            BEGIN;
                CREATE TEMP TABLE {TABLE_NAME}_backup AS SELECT * FROM {TABLE_NAME};
                {cd.TABLE_CONFIG[table]['drop_sql']}
                \\i '{cd.TABLE_CONFIG[table]['create_sql_file_path'].as_posix()}';
                INSERT INTO {TABLE_NAME} SELECT * FROM {TABLE_NAME}_backup;
            COMMIT;
        """

        tmp_sql_file = othr.create_tmp_sql_file(sql_content=transaction)

        try:
            exe.execute_query(file=tmp_sql_file, header=False, capture=True)
        finally:
            if os.path.exists(tmp_sql_file):
                os.remove(tmp_sql_file)
        
        data_status = "DATA KEPT."

    else:
        cd.drop_table(table=table, print_confirmation=False)
        cd.create_table(table=table, print_confirmation=False)
        data_status = "DATA LOST."
    
    sqnc.update_sequence()

    ff.print_colored(text=f"TABLE '{TABLE_NAME}' REFRESHED. {data_status}\n", color="GREEN")


def _determine_keep_data(keep_data) -> str | None:
    #1 - Validating 'keep_data' if already typed
    #2 - Using config.json default 'keep_data' value
    
    # Validate 'keep_data' typed by user
    if keep_data:
        validated, validation_message = vv.validate_choice(choice=keep_data, valid_options=DATA_OPTIONS, choice_name="KEEP_DATA")
        if not validated:
            # if validation_message: --> It can't happen here because even if 'keep_data' is not typed, default value is taken from config.json
            ff.print_colored(text=f"{validation_message}\n", color="RED")
            return None
        return keep_data
    
    # Taking value from config.json
    CONFIG_KEEP_DATA = cnfg.config['command']['refresh']['keep_data_on_refresh']
    return KEEP_DATA_OPTIONS[0] if CONFIG_KEEP_DATA else LOSE_DATA_OPTIONS[0]
