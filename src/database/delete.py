import config as cnfg

import utils.formatter as ff
import utils.inputter as ii
import utils.validator as vv

import database.tools.executor as exe
import database.tools.state as stt


TABLE_CONFIG = {
    cnfg.PRIMARY_TB_ALIAS: {
        'delete_sql': "DELETE FROM timings WHERE id = {id};"
    },
    cnfg.HISTORY_TB_ALIAS: {
        'delete_sql': "DELETE FROM timings_history WHERE id = {id};"
    }
}


def delete_manager(target, record_id=None):    
    # Delete from both tables. Same ID
    if target == cnfg.EVERYTHING_ALIAS:
        
        # Check if DB/TABLES exist
        if not stt.verify_db_exists_state(bad_info_message=ff.colorize(text="DELETE NOT POSSIBLE. {rest}\n", color="YELLOW")):
            return
        
        # ID not typed
        if not record_id:
            record_id = ii.get_user_input(prompt="ID")
            
            # Change of mind
            if not record_id:
                print()
                return
            # Validating ID
            if not _check_id_from_user(record_id=record_id):
                return

        print()
        delete_manager(target=cnfg.PRIMARY_TB_ALIAS, record_id=record_id)
        delete_manager(target=cnfg.HISTORY_TB_ALIAS, record_id=record_id)
        return
    
    
    # Check table name
    if target not in cnfg.BOTH_TABLES:
        ff.print_colored(text=f"INVALID TABLE '{target}'.\n", color="RED")
        return

    # Check if DB/TABLE exists
    if not stt.check_db_exists_state(
        table=cnfg.get_tb_name(table=target),
        info_message=ff.colorize(text="DELETE NOT POSSIBLE. {rest}\n", color="YELLOW")
    )[0]:
        return
    
    # ID not typed - Asking for it
    if not record_id:
        record_id = ii.get_user_input(prompt="ID")
        # Change of mind
        if not record_id:
            print()
            return

    # Validate ID
    if not _check_id_from_user(record_id=record_id):
        return
    
    _delete_exec(table=target, record_id=int(record_id))

def _delete_exec(table, record_id) -> None:
    result = exe.execute_query(sql=TABLE_CONFIG[table]['delete_sql'].format(id=record_id), header=False, capture=True)

    if "DELETE 0" in result.stdout.strip():
        ff.print_colored(text=f"RECORD '{record_id}' NOT FOUND IN TABLE '{cnfg.get_tb_name(table=table)}'.\n", color="YELLOW")
        return
    
    ff.print_colored(text=f"RECORD '{record_id}' DELETED FROM TABLE '{cnfg.get_tb_name(table=table)}'.\n", color="GREEN")


def _check_id_from_user(record_id) -> bool:
    id_ok = vv.validate_type(variable=record_id, expected_type="number")
    if not id_ok:
        print(
            f"{ff.colorize(text=f"INVALID ID '{record_id}'.", color="RED")} "
            f"{ff.colorize(text=" WHOLE POSITIVE NUMBER EXPECTED.", color="YELLOW")}\n"
        )
    return id_ok
