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

# HELP command
def display_main_menu(commands_dict) -> None:
    MAIN_MENU_WIDTH = 30
    
    if not commands_dict:
        ff.print_colored(text="NO COMMANDS AVAILABLE.\n", color="YELLOW")
        return
    
    header_text = "COMMANDS"
    
    items = []
    for i, (command, data) in enumerate(commands_dict.items(), 1):
        emoji = data.get('emoji', '•')
        left_text = f"{emoji} {command}"
        right_text = f"#{i:02d}"
        items.append((left_text, right_text))
    
    draw_menu_with_header(header_text, items, MAIN_MENU_WIDTH)
    print()

def display_command_arguments(command, commands_dict) -> None:
    ARGUMENTS_MENU_WIDTH = 40
    
    # if command not in commands_dict:
    #     ff.print_colored(text="COMMAND DOESN'T EXIST.\n", color="YELLOW")
    #     return
    
    command_data = commands_dict[command]
    
    emoji = command_data.get('emoji', '•')
    args_dict = command_data['args']
    
    header_text = f"{emoji} {command.upper()} ARGUMENTS"
    
    items = []
    
    for key in args_dict:
        arg_combo = args_dict[key]
        
        if not arg_combo:
            left_text = command
        else:
            left_text = f"{command} {' '.join(arg_combo)}"
        
        right_text = f"#{key}"
        items.append((left_text, right_text))
    
    draw_menu_with_header(header_text, items, ARGUMENTS_MENU_WIDTH, add_spacing=True)
    print()
# HELP command

def get_display_width(text) -> int:
    width = 0
    for char in text:
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            width += 2
        else:
            width += 1
    return width

def draw_menu_with_header(header_text, items, fixed_width, add_spacing=False) -> None:
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'
    
    border = "═" * fixed_width
    header_display_width = get_display_width(header_text)
    padding_total = fixed_width - header_display_width
    padding_left = padding_total // 2
    padding_right = padding_total - padding_left
    
    print(f"{BOLD}")
    print(f"    ╔{border}╗")
    print(f"    ║{' ' * padding_left}{header_text}{' ' * padding_right}║")
    print(f"    ╚{border}╝")
    print(f"{RESET}")
    
    for i, (left_text, right_text) in enumerate(items):
        left_display_width = get_display_width(left_text)
        right_display_width = get_display_width(right_text)
        
        dots_count = fixed_width - left_display_width - right_display_width
        dots = f"{DIM}{'.' * max(0, dots_count)}{RESET}"
        
        print(f"    {BOLD}{left_text}{RESET}{dots}{DIM}{right_text}{RESET}")
        
        if add_spacing and i < len(items) - 1:
            print()
