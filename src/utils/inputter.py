def get_user_input(prompt="Select an option", lowercase=True) -> str:
    user_input = input(f"◇ {prompt}: ").strip()

    if lowercase:
        return user_input.lower()
    return user_input