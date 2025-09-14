def get_user_input(symbol='◇', prompt="Select an option", with_colon=True, lowercase=True) -> str:
    user_input = input(f"{symbol} {prompt}{':' if with_colon else ''} ").strip()

    if lowercase:
        return user_input.lower()
    return user_input

