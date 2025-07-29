import config as cnfg


def get_db_exists_state(table=None, must_exists=True, include_table_name=False) -> tuple[bool, str]:
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
