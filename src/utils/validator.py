def validate_choice(choice, valid_options, choice_name="") -> tuple[bool, str]:
    choice_name_frmtd = f"{choice_name} " if choice_name else ""
    
    if not choice:
        return False, ""
    
    if choice not in valid_options:
        return False, f"INVALID {choice_name_frmtd}CHOICE '{choice}'."
    
    return True, f"VALID {choice_name_frmtd}CHOICE."
