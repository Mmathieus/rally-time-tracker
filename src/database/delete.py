import config as cnfg

import utils.formatter as ff
import utils.inputter as ii

import database.tools.executor as exe
import database.tools.other as othr


TABLE_CONFIG = {
    cnfg.PRIMARY_TB_ALIAS: {
        'delete_sql': "DELETE FROM timings WHERE id = {id};"
    },
    cnfg.HISTORY_TB_ALIAS: {
        'delete_sql': "DELETE FROM timings_history WHERE id = {id};"
    }
}


def delete_manager(table, record_id=None):
    if table not in cnfg.BOTH_TABLES:
        ff.print_colored(text=f"INVALID TABLE '{table}'.\n", color="RED")
        return

    # Check if DB/TABLE exists
    all_ok, info_message = othr.get_db_exists_state(table=cnfg.get_tb_name(table=table))
    if not all_ok:
        ff.print_colored(text=f"DELETE ABORTED. {info_message}\n", color="YELLOW")
        return
    
    if not record_id:
        record_id = ii.get_user_input(prompt="ID")
        if not record_id:
            print()
            return

    if not record_id.isdigit():
        print(
            f"{ff.colorize(text=f"INVALID ID '{record_id}'.", color="RED")} "
            f"{ff.colorize(text=" WHOLE POSITIVE NUMBER EXPECTED.", color="YELLOW")}\n"
        )
        return
    
    _delete_exec(table=table, record_id=int(record_id))

def _delete_exec(table, record_id) -> None:
    result = exe.execute_query(sql=TABLE_CONFIG[table]['delete_sql'].format(id=record_id), header=False, capture=True)

    if "DELETE 0" in result.stdout.strip():
        ff.print_colored(text=f"DELETE UNSUCCESSFUL. RECORD '{record_id}' NOT FOUND.\n", color="YELLOW")
        return
    
    ff.print_colored(text=f"RECORD {record_id} DELETED SUCCESSFULLY.\n", color="GREEN")
