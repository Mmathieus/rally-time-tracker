import config as cnfg

import utils.formatter as ff
import utils.inputter as ii
import utils.other as oo

import database.tools.executor as exe


TIMINGS_ALIAS = cnfg.config['table_references']['timings']
TIMINGS_HISTORY_ALIAS = cnfg.config['table_references']['timings_history']

TABLE_CONFIG = {
    TIMINGS_ALIAS: {
        'table_name': "timings",
        'delete_sql': "DELETE FROM timings WHERE id = {id};"
    },
    TIMINGS_HISTORY_ALIAS: {
        'table_name': "timings_history",
        'delete_sql': "DELETE FROM timings_history WHERE id = {id};"
    }
}

def delete_manager(table, record_id=None):
    if table not in (TIMINGS_ALIAS, TIMINGS_HISTORY_ALIAS):
        ff.print_colored(text=f"INVALID TABLE '{table}'.\n", color="YELLOW")
        return

    all_ok, info_message = oo.get_db_exists_state(table=TABLE_CONFIG[table]['table_name'])
    if not all_ok:
        ff.print_colored(text=f"DELETE ABORTED. {info_message}\n", color="YELLOW")
        return
    
    if not record_id:
        record_id = ii.get_user_input(prompt="ID")
        if not record_id:
            print()
            return

    if not record_id.isdigit():
        ff.print_colored(text="INVALID ID. WHOLE POSITIVE NUMBER EXPECTED.\n")
        return
    
    _delete_exec(table=table, record_id=int(record_id))

def _delete_exec(table, record_id) -> None:
    result = exe.execute_query(sql=TABLE_CONFIG[table]['delete_sql'].format(id=record_id), header=False, capture=True)

    if "DELETE 0" in result.stdout.strip():
        ff.print_colored(text=f"DELETE UNSUCCESSFUL. RECORD '{record_id}' NOT FOUND.\n", color="YELLOW")
        return
    
    ff.print_colored(text=f"RECORD {record_id} DELETED SUCCESSFULLY.\n", color="GREEN")
