def get_user_input(prompt="Select an option", symbol='◇', with_colon=True, lowercase=True) -> str:
    user_input = input(f"{symbol} {prompt}{':' if with_colon else ''} ").strip()

    if lowercase:
        return user_input.lower()
    return user_input

def parse_command_input(input_string) -> tuple[str, list[str], int]:
    parts = input_string.strip().split()
    
    if not parts:
        return "", [], 0
    
    command = parts[0]
    args = parts[1:] if len(parts) > 1 else []
    
    return command, args, len(args)
