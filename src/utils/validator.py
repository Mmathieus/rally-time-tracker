import utils.formatter as ff
from config import config

def validate_choice(choice, valid_options, choice_type) -> bool:
    if not choice:
        return False
    
    if choice not in valid_options:
        ff.print_colored(text=f"INVALID {choice_type} CHOICE '{choice}'.\n", color="RED")
        return False
    return True

def validate_db_status(table=None, db_print=True, table_print=True):
    if not config['db_status']['database']:
        if db_print:
            ff.print_colored(text=f"DATABASE '{config['db_connection']['database']}' NOT FOUND.\n", color="RED")
        return False
    
    if table and not config['db_status'][table]:
        if table_print:
            ff.print_colored(text=f"TABLE '{table}' NOT FOUND.\n", color="RED")
        return False
    return True