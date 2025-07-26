import config as cnfg

import utils.formatter as ff

import database.tools.status as stts

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


def display_main_menu(commands_dict):
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

def display_command_arguments(command_name, commands_dict):
    ARGUMENTS_MENU_WIDTH = 40
    
    # if command_name not in commands_dict:
    #     ff.print_colored(text="COMMAND DOESN'T EXIST.\n", color="YELLOW")
    #     return
    
    command_data = commands_dict[command_name]
    
    emoji = command_data.get('emoji', '•')
    args_dict = command_data['args']
    
    header_text = f"{emoji} {command_name.upper()} ARGUMENTS"
    
    items = []
    
    for key in args_dict:
        arg_combo = args_dict[key]
        
        if not arg_combo:
            left_text = command_name
        else:
            left_text = f"{command_name} {' '.join(arg_combo)}"
        
        right_text = f"#{key}"
        items.append((left_text, right_text))
    
    draw_menu_with_header(header_text, items, ARGUMENTS_MENU_WIDTH, add_spacing=True)
    print()


def get_display_width(text):
    width = 0
    for char in text:
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            width += 2
        else:
            width += 1
    return width

def draw_menu_with_header(header_text, items, fixed_width, add_spacing=False):
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


def get_text_without_ansi(text):
    import re
    ansi_escape = re.compile(r'\033\[[0-9;]*m')
    return ansi_escape.sub('', text)

def calculate_padding(line, width):
    clean_text = get_text_without_ansi(line)
    display_width = get_display_width(clean_text)
    return width - display_width - 1

def format_size(bytes_size):
    if bytes_size is None:
        return "N/A"
    
    if bytes_size >= 1000:
        kb_size = bytes_size / 1024.0
        if kb_size >= 1000:
            mb_size = kb_size / 1024.0
            if mb_size >= 1000:
                gb_size = mb_size / 1024.0
                return f"{gb_size:.2f} GB"
            return f"{mb_size:.2f} MB"
        return f"{kb_size:.2f} KB"
    
    return f"{bytes_size:.2f} B"

def print_dashboard(data=None, with_new_db_state=True):
    data = cnfg.db_state
    
    if with_new_db_state:
        stts.get_current_db_state()

    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    DASHBOARD_WIDTH = 70
    
    print("╭" + "─" * (DASHBOARD_WIDTH-2) + "╮")
    print(f"│{BOLD}{'DASHBOARD':^{DASHBOARD_WIDTH-2}}{RESET}│")
    print("├" + "─" * (DASHBOARD_WIDTH-2) + "┤")
    
    db_exists = data.get('database', {}).get('exists', False)
    db_size = data.get('database', {}).get('size', 0)
    
    status_color = GREEN if db_exists else RED
    status_symbol = "✓" if db_exists else "✗"
    
    print(f"│ {BOLD}DATABASE{RESET}" + " " * (DASHBOARD_WIDTH - get_display_width(f" DATABASE") - 2) + "│")
    print("│" + " " * (DASHBOARD_WIDTH-2) + "│")
    
    db_line = f"│   {status_color}{status_symbol}{RESET} {cnfg.config['db_connection']['database']}"
    padding = calculate_padding(db_line, DASHBOARD_WIDTH)
    print(f"{db_line}{' ' * padding}│")
    print("│" + " " * (DASHBOARD_WIDTH-2) + "│")
    
    if db_exists:
        size_line = f"│       Size: {YELLOW}{format_size(db_size)}{RESET}"
        padding = calculate_padding(size_line, DASHBOARD_WIDTH)
        print(f"{size_line}{' ' * padding}│")
        print("│" + " " * (DASHBOARD_WIDTH-2) + "│")
    print("├" + "─" * (DASHBOARD_WIDTH-2) + "┤")
    
    print(f"│ {BOLD}TABLES{RESET}" + " " * (DASHBOARD_WIDTH - get_display_width(f" TABLES") - 2) + "│")
    print("│" + " " * (DASHBOARD_WIDTH-2) + "│")
    
    table_names = ['timings', 'timings_history']
    
    for table_name in table_names:
        table_info = data.get(table_name, {})
        exists = table_info.get('exists', False)
        records = table_info.get('records', 0)
        total_size = table_info.get('size', 0)
        data_size = table_info.get('data_size', 0)
        
        status_color = GREEN if exists else RED
        status_symbol = "✓" if exists else "✗"
        
        table_line = f"│   {status_color}{status_symbol}{RESET} {BOLD}{table_name}{RESET}"
        padding = calculate_padding(table_line, DASHBOARD_WIDTH)
        print(f"{table_line}{' ' * padding}│")
        print("│" + " " * (DASHBOARD_WIDTH-2) + "│")
        
        if exists:
            records_line = f"│       Records: {records}"
            padding = calculate_padding(records_line, DASHBOARD_WIDTH)
            print(f"{records_line}{' ' * padding}│")
            
            total_line = f"│       Size: {YELLOW}{format_size(total_size)}{RESET}"
            padding = calculate_padding(total_line, DASHBOARD_WIDTH)
            print(f"{total_line}{' ' * padding}│")
            
            data_size_line = f"│         └─ Data: {format_size(data_size)}"
            padding = calculate_padding(data_size_line, DASHBOARD_WIDTH)
            print(f"{data_size_line}{' ' * padding}│")
        
        print("│" + " " * (DASHBOARD_WIDTH-2) + "│")
    
    print("╰" + "─" * (DASHBOARD_WIDTH-2) + "╯" + '\n')


