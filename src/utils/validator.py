import utils.formatter as ff


def validate_choice(choice, valid_options) -> bool:
    if not choice:
        return False
    
    if choice not in valid_options:
        ff.print_colored(text=f"INVALID CHOICE '{choice}'.\n", color="RED")
        return False
    return True
