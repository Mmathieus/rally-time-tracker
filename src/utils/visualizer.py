# NOTE Display a nice menu with options and gets user input.
def get_input__display_menu(title, options, prompt="Select an option", lowercase=True) -> str:
    print(f"\n╭{'─' * (len(title) + 4)}╮")
    print(f"│  {title}  │")
    print(f"╰{'─' * (len(title) + 4)}╯")
    
    for option in options:
        print(f"  ○ {option}")
    
    print()
    user_input = input(f"◇ {prompt}: ").strip()
    return user_input.lower() if lowercase else user_input