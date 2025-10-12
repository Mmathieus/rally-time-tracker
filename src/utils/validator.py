def validate_choice(choice, valid_options, choice_name="") -> tuple[bool, str]:
    choice_name_frmtd = f"{choice_name} " if choice_name else ""
    
    if not choice:
        return False, ""
    
    if choice not in valid_options:
        return False, f"INVALID {choice_name_frmtd}CHOICE '{choice}'."
    
    return True, f"VALID {choice_name_frmtd}CHOICE."


def validate_type(variable, expected_type) -> bool:
    types = {
        'int': int,
        'str': str,
        'bool': bool,
        'list': list
    }

    # Check bool first before int (because bool is subclass of int in Python)
    if expected_type == "int" and isinstance(variable, bool):
        return False
    
    return isinstance(variable, types[expected_type])
