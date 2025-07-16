def upper_casing(term):
    term = term.strip()
    return '-'.join([word.capitalize() for word in term.split('-')])


colors = {
    "RED" : "\033[31m",
    "CYAN" : "\033[36m",
    "GREEN" : "\033[32m",
    "YELLOW" : "\033[33m",
    "MAGENTA" : "\033[35m",
    "RESET" : "\033[0m"
}

def colorize(text, color):
    return f"{colors[color]}{text}{colors['RESET']}"

def print_colored(text, color, really_print=True):
    if really_print:
        print(colorize(text, color))
