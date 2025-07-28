import config as cnfg


def get_db_exists_state(table=None, must_exists=True, include_table_name=False) -> tuple[bool, str | None]:
    # IF db/table must exists    -> then the problem is that it DOESN'T EXISTS.
    # IF db/table mustn't exists -> then the problem is that it EXISTS.
    exists_text = "DOESN'T EXIST" if must_exists else "ALREADY EXISTS"

    status_message = f"DATABASE {exists_text}."
    
    if not cnfg.db_state['database']['exists']:
        return False, status_message
    
    if table:
        table_name = f"'{table}' " if include_table_name else ""
        status_message = f"TABLE {table_name}{exists_text}."
        
        if not cnfg.db_state[table]['exists']:
            return False, status_message
    
    return True, status_message
