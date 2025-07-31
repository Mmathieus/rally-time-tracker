import utils.formatter as ff


def validate_choice(choice, valid_options, print_error=True) -> bool:
    if not choice:
        return False
    
    if choice not in valid_options:
        if print_error:
            ff.print_colored(text=f"INVALID CHOICE '{choice}'.\n", color="RED")
        return False
    return True
