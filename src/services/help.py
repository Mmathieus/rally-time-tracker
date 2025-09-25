import config as cnfg

import utils.formatter as ff
import utils.menu as mm


DATABASE_COMMANDS_COUNT = 11

MAIN_MENU_WIDTH = cnfg.config['ui']['help']['main_menu_width']
MAIN_MENU_COLUMN_SPACING = cnfg.config['ui']['help']['main_menu_column_spacing']

COMMANDS_MENU_WIDTH = cnfg.config['ui']['help']['arguments_menu_width']


###- THANKS TO Claude Sonnet 4 FOR THIS -###

def display_commands_menu(commands_dict) -> None:
    if not commands_dict:
        ff.print_colored(text="NO COMMANDS AVAILABLE.\n", color="YELLOW")
        return
    
    commands_list = list(commands_dict.items())
    
    database_commands = commands_list[:DATABASE_COMMANDS_COUNT]
    program_commands = commands_list[DATABASE_COMMANDS_COUNT:]
    
    # Create columns data
    columns = []
    if database_commands:
        db_items = []
        for i, (command, data) in enumerate(database_commands, 1):
            emoji = data.get('emoji', '•')
            left_text = f"{emoji} {command}"
            right_text = f"#{i:02d}"
            db_items.append((left_text, right_text))
        columns.append(("DATABASE COMMANDS", db_items))
    
    if program_commands:
        prog_items = []
        for i, (command, data) in enumerate(program_commands, DATABASE_COMMANDS_COUNT + 1):
            emoji = data.get('emoji', '•')
            left_text = f"{emoji} {command}"
            right_text = f"#{i:02d}"
            prog_items.append((left_text, right_text))
        columns.append(("PROGRAM COMMANDS", prog_items))
    
    # Display columns side by side
    _display_columns_side_by_side(columns, MAIN_MENU_WIDTH)
    print()

def display_command_arguments_menu(command, commands_dict) -> None:
    if command not in commands_dict:
        ff.print_colored(text=f"INVALID COMMAND '{command}'.\n", color="RED")
        return
    
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
    
    _draw_header_with_menu_options(header_text, items, COMMANDS_MENU_WIDTH, add_spacing=True)
    print()

def _display_columns_side_by_side(columns, column_width) -> None:
    """Display multiple columns side by side with universal spacing"""
    if not columns:
        return
    
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'
    
    # Generate headers for all columns
    headers = []
    borders = []
    for header_text, _ in columns:
        border = "═" * column_width
        header_display_width = mm.get_display_width(header_text)
        padding_total = column_width - header_display_width
        padding_left = padding_total // 2
        padding_right = padding_total - padding_left
        
        header_lines = [
            f"╔{border}╗",
            f"║{' ' * padding_left}{header_text}{' ' * padding_right}║",
            f"╚{border}╝"
        ]
        headers.append(header_lines)
        borders.append(border)
    
    # Print headers side by side
    print(f"{BOLD}")
    for line_idx in range(3):  # 3 lines per header (top, middle, bottom)
        line_parts = []
        for col_idx, header_lines in enumerate(headers):
            line_parts.append(f"    {header_lines[line_idx]}")
            if col_idx < len(headers) - 1:  # Add spacing between columns
                line_parts.append(" " * MAIN_MENU_COLUMN_SPACING)
        print("".join(line_parts))
    print(f"{RESET}")
    
    # Find max number of items across all columns
    max_items = max(len(items) for _, items in columns) if columns else 0
    
    # Print items side by side with original spacing
    for item_idx in range(max_items):
        line_parts = []
        for col_idx, (_, items) in enumerate(columns):
            if item_idx < len(items):
                left_text, right_text = items[item_idx]
                left_display_width = mm.get_display_width(left_text)
                right_display_width = mm.get_display_width(right_text)
                
                dots_count = column_width - left_display_width - right_display_width
                dots = f"{DIM}{'.' * max(0, dots_count)}{RESET}"
                
                column_content = f"    {BOLD}{left_text}{RESET}{dots}{DIM}{right_text}{RESET}"
            else:
                # Empty column content if this column has fewer items
                column_content = "    " + " " * column_width
            
            line_parts.append(column_content)
            if col_idx < len(columns) - 1:  # Add spacing between columns
                line_parts.append(" " * MAIN_MENU_COLUMN_SPACING)
        
        print("".join(line_parts))
        
        # Add empty line after each item (original spacing)
        if item_idx < max_items - 1:
            print()

def _draw_header_with_menu_options(header_text, items, fixed_width, add_spacing=False) -> None:
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'
    
    border = "═" * fixed_width
    header_display_width = mm.get_display_width(header_text)
    padding_total = fixed_width - header_display_width
    padding_left = padding_total // 2
    padding_right = padding_total - padding_left
    
    print(f"{BOLD}")
    print(f"    ╔{border}╗")
    print(f"    ║{' ' * padding_left}{header_text}{' ' * padding_right}║")
    print(f"    ╚{border}╝")
    print(f"{RESET}")
    
    for i, (left_text, right_text) in enumerate(items):
        left_display_width = mm.get_display_width(left_text)
        right_display_width = mm.get_display_width(right_text)
        
        dots_count = fixed_width - left_display_width - right_display_width
        dots = f"{DIM}{'.' * max(0, dots_count)}{RESET}"
        
        print(f"    {BOLD}{left_text}{RESET}{dots}{DIM}{right_text}{RESET}")
        
        if add_spacing and i < len(items) - 1:
            print()
