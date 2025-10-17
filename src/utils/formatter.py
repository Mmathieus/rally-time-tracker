import unicodedata


def to_pascal_kebab_case(term) -> str:
    term = term.strip().lower()
    return '-'.join([word.capitalize() for word in term.split('-')])


colors = {
    "RED": "\033[31m",
    "CYAN": "\033[36m",
    "BLUE": "\033[34m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "MAGENTA": "\033[35m",
    "RESET": "\033[0m"
}

formats = {
    "BOLD": "\033[1m",
    "DIM": "\033[2m"
}

def print_colored(text, color=None, really_print=True) -> None:
    if really_print:
        if color:
            print(colorize(text, color))
        else:
            print(text)

def colorize(text, color) -> str:
    if color:
        return f"{colors[color]}{text}{colors['RESET']}"
    else:
        return text


def display_menu(title="VALID OPTIONS", options=None) -> None:
    if not options:
        print_colored(text="NO OPTIONS AVAILABLE\n", color="YELLOW")
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