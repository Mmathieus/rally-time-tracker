import utils.formatter as ff

import unicodedata
import re


def display_menu(title="VALID OPTIONS", options=None) -> bool:
    if not options:
        ff.print_colored(text="NO OPTIONS AVAILABLE\n", color="YELLOW")
        return False
    
    print(f"\n╭{'─' * (len(title) + 4)}╮")
    print(f"│  {title}  │")
    print(f"╰{'─' * (len(title) + 4)}╯")
    
    for option in options:
        print(f"  ○ {option}")
    print()
    return True


def get_display_width(text) -> int:
    # Remove ANSI escape codes first
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    clean_text = ansi_escape.sub('', text)
    
    width = 0
    for char in clean_text:
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            width += 2
        else:
            width += 1
    return width