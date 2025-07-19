import utils.formatter as ff

def display_menu(title="VALID OPTIONS", options=None) -> None:
    if not options:
        ff.print_colored(text="NO OPTIONS AVAILABLE\n", color="YELLOW")
        return
    
    print(f"\n╭{'─' * (len(title) + 4)}╮")
    print(f"│  {title}  │")
    print(f"╰{'─' * (len(title) + 4)}╯")
    
    for option in options:
        print(f"  ○ {option}")
    print()