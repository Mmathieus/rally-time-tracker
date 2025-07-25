def upper_casing(term) -> str:
    term = term.strip().lower()
    return '-'.join([word.capitalize() for word in term.split('-')])


_colors = {
    "RED" : "\033[31m",
    "CYAN" : "\033[36m",
    "GREEN" : "\033[32m",
    "YELLOW" : "\033[33m",
    "MAGENTA" : "\033[35m",
    "RESET" : "\033[0m"
}

def print_colored(text, color, really_print=True) -> None:
    if really_print:
        print(colorize(text, color))

def colorize(text, color) -> str:
    return f"{_colors[color]}{text}{_colors['RESET']}"
