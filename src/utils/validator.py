import utils.formatter as ff
from config import config

def validate_choice(choice, valid_options, choice_type) -> bool:
    if not choice:
        return False
    
    if choice not in valid_options:
        ff.print_colored(text=f"INVALID {choice_type} CHOICE '{choice}'.\n", color="RED")
        return False
    return True

def validate_db_status(table=None, db_print=True, table_print=True, must_exist=True) -> tuple[bool, str | None]:
    status_message = ""
    
    # IF db/table must exists    -> then the problem is that it DOESN'T EXISTS.
    # IF db/table mustn't exists -> then the problem is that it EXISTS.
    exists_text = "DOESN'T EXIST" if must_exist else "ALREADY EXISTS"
    
    if not config['db_status']['database']:
        if db_print:
            status_message = f"DATABASE '{config['db_connection']['database']}' {exists_text}."
        return False, status_message
    
    if table and not config['db_status'][table]:
        if table_print:
            status_message = f"TABLE '{table}' {exists_text}."
        return False, status_message
    
    return True, None