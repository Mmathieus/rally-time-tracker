def display_menu(title="VALID OPTIONS", options=None) -> None:
    print(f"\n╭{'─' * (len(title) + 4)}╮")
    print(f"│  {title}  │")
    print(f"╰{'─' * (len(title) + 4)}╯")
    
    for option in options:
        print(f"  ○ {option}")
    print()