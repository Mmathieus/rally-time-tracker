import utils.formatter as ff
import unicodedata


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

def get_display_width(text) -> int:
    width = 0
    for char in text:
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            width += 2
        else:
            width += 1
    return width
