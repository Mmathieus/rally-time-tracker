import config as cnfg

import utils.formatter as ff
import utils.other as oo
import utils.validator as vv

import database.create__drop as cd
import database.tools.executor as exe
import database.tools.sequence as sqnc
import database.tools.tmp_file as tmpfl

import os


KEEP_DATA_OPTIONS = cnfg.config['command']['refresh']['data_handling']['keep']
LOSE_DATA_OPTIONS = cnfg.config['command']['refresh']['data_handling']['lose']
DATA_OPTIONS = KEEP_DATA_OPTIONS + LOSE_DATA_OPTIONS


def refresh_manager(table, keep_data=None) -> None:
    if table not in cnfg.BOTH_TABLES:
        ff.print_colored(text=f"INVALID TABLE NAME '{table}'.\n", color="RED")
        return
    
    # Check if DB/TABLE exists
    all_ok, info_message = oo.get_db_exists_state(table=cnfg.get_tb_name(table=table))
    if not all_ok:
        ff.print_colored(text=f"TABLE '{cnfg.get_tb_name(table=table)}' NOT REFRESHED. {info_message}\n", color="YELLOW")
        return
    
    if not keep_data:
        CONFIG_KEEP_DATA = cnfg.config['command']['refresh']['keep_data_on_refresh']
        keep_data = KEEP_DATA_OPTIONS[0] if CONFIG_KEEP_DATA else LOSE_DATA_OPTIONS[0]
    
    validated, validation_message = vv.validate_choice(choice=keep_data, valid_options=DATA_OPTIONS, choice_name="KEEP_DATA")
    if not validated:
        ff.print_colored(text=f"{validation_message}\n", color="RED")
        return
    
    _refresh_table(table=table, keep_data=keep_data)

def _refresh_table(table, keep_data) -> None:
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

        tmp_sql_file = tmpfl.create_tmp_sql_file(sql_content=transaction)

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