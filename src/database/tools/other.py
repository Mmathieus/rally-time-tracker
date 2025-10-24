import config as cnfg
import utils.formatter as ff
import tempfile


# Used when 'command 'all'' is called to verify DB/TABLES existance based on given arguments
def verify_db_exists_state(both_required=False, must_exist=True, include_table_name=True, bad_info_message="") -> bool:
    
    # Check primary table
    primary_ok, primary_message = _get_db_exists_state(table=cnfg.PRIMARY_TB_NAME, must_exists=must_exist, include_table_name=include_table_name)
    # Primary table not ok
    if not primary_ok:
        # Something wrong with database -> done here
        if "DATABASE" in primary_message:
            print(f"{bad_info_message.format(rest=primary_message)}")
            return False
    
    # Check history table
    history_ok, history_message = _get_db_exists_state(table=cnfg.HISTORY_TB_NAME, must_exists=must_exist, include_table_name=include_table_name)
    

    # Determine tables count message
    tables_count_message = "NEITHER TABLE EXISTS." if must_exist else "BOTH TABLES EXIST."


    # At least 1 is required but both are not OK
    if not both_required and (not primary_ok and not history_ok):
        print(bad_info_message.format(rest=tables_count_message))
        return False


    # Both are required and both aren't OK
    if both_required and (not primary_ok and not history_ok):
        print(bad_info_message.format(rest=tables_count_message))
        return False
    
    # Both are required and only primary is OK
    if both_required and (primary_ok and not history_ok):
        print(bad_info_message.format(rest=history_message))
        return False

    # Both are required and only history is OK
    if both_required and (not primary_ok and history_ok):
        print(bad_info_message.format(rest=primary_message))
        return False
    
    return True


# Used in specific files to check if DB/TABLES are present | Gets result from Core function and determines output based on given arguments
def evaluate_db_exists_state(table=None, must_exists=True, include_table_name=True, info_message="", info_mesage_decision="print") -> tuple[bool, str]:
    all_ok, existance_message = _get_db_exists_state(table=table, must_exists=must_exists, include_table_name=include_table_name)
    
    returning_string = info_message.format(rest=existance_message)

    if all_ok:
        return True, returning_string
    
    if info_mesage_decision == "return":
        return False, returning_string
    
    if info_mesage_decision == "print":
        print(returning_string)
        return False, returning_string
    
    ff.print_colored(text=f"SYSTEM ERROR: wrong argument 'info_message_decision': {info_mesage_decision}\n", color="RED")
    return False, "ERROR"


# Core function -> returns if its 'ALL OK' and 'info message' 
def _get_db_exists_state(table=None, must_exists=True, include_table_name=True) -> tuple[bool, str]:
    db_exists = cnfg.db_state['database']['exists']
    
    # Checking only Database existance
    if not table:
        # Database must exists AND it does
        if must_exists and db_exists:
            return True, "DATABASE ALREADY EXISTS."
        # Database must exists BUT it does't
        elif must_exists and not db_exists:
            return False, "DATABASE DOESN'T EXIST."
        # Database musn't exists BUT it does
        elif not must_exists and db_exists:
            return False, "DATABASE ALREADY EXISTS."
        # Database musn't exists AND it doesn't
        elif not must_exists and not db_exists:
            return True, "DATABASE DOESN'T EXIST."
    
    # Checking Table -> Database must exists in every circumstances
    if not db_exists:
        return False, "DATABASE DOESN'T EXIST."
    
    table_exists = cnfg.db_state[table]['exists']
    table_name = f"'{table}' " if include_table_name else ""

    # Table must exists AND it does
    if must_exists and table_exists:
        return True, f"TABLE {table_name}ALREADY EXISTS."
    # Table must exists BUT it does't
    elif must_exists and not table_exists:
        return False, f"TABLE {table_name}DOESN'T EXIST."
    # Table musn't exists BUT it does
    elif not must_exists and table_exists:
        return False, f"TABLE {table_name}ALREADY EXISTS."
    # Table musn't exists AND it doesn't
    elif not must_exists and not table_exists:
        return True, f"TABLE {table_name}DOESN'T EXIST."


def create_tmp_sql_file(sql_content) -> str:
    tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8')
    tmp_file.write(sql_content)
    tmp_file.close()
    return tmp_file.name
