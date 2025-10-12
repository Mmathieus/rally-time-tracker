import config as cnfg

import utils.formatter as ff
import utils.menu as mm
import utils.validator as vv


DATABASE_COMMANDS_COUNT = 11

MAIN_MENU_COLUMN_WIDTH = cnfg.config['ui']['help']['main_menu_column_width']
MAIN_MENU_COLUMNS_SPACING = cnfg.config['ui']['help']['main_menu_columns_spacing']

COMMANDS_ARGUMENTS_MENU_WIDTH = cnfg.config['ui']['help']['arguments_menu_width']

BOLD = ff.formats['BOLD']
DIM = ff.formats['DIM']
RESET = ff.colors['RESET']


### - Thanks to Claude Sonnet 4 for this (95%) - ###


def display_commands_menu(commands_dict) -> None:
    if not commands_dict:
        ff.print_colored(text="NO COMMANDS AVAILABLE.\n", color="YELLOW")
        return
    
    commands_list = list(commands_dict.items())
    
    database_commands = commands_list[:DATABASE_COMMANDS_COUNT]
    program_commands = commands_list[DATABASE_COMMANDS_COUNT:]
    
    # Prepare columns
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
    _display_columns_side_by_side(columns)
    print()

def _display_columns_side_by_side(columns) -> None:
    if not columns:
        return

    global MAIN_MENU_COLUMNS_SPACING
    # Validate config value
    MAIN_MENU_COLUMNS_SPACING = _validate_config_value(value=MAIN_MENU_COLUMNS_SPACING, default=3, min_value=1)


    # Calculate final widths for each column
    column_widths = []
    for header_text, items in columns:
        width = _calculate_column_width(header_text, items)
        column_widths.append(width)
    
    # Generate headers for all columns
    headers = []
    for col_idx, (header_text, items) in enumerate(columns):
        column_width = column_widths[col_idx]
        # Minus left and right corners
        border = "═" * (column_width - 2)
        
        # Number of spaces for padding
        header_display_width = mm.get_display_width("║") + 1 + mm.get_display_width(header_text) + 1 + mm.get_display_width("║")
        padding_total = column_width - header_display_width
        padding_left = padding_total // 2
        padding_right = padding_total - padding_left
        
        header_lines = [
            f"╔{border}╗",
            f"║{' ' * padding_left} {header_text} {' ' * padding_right}║",
            f"╚{border}╝"
        ]
        headers.append(header_lines)
    
    # Print headers side by side
    print(f"{BOLD}")
    for line_idx in range(3):
        line_parts = []
        for col_idx, header_lines in enumerate(headers):
            if col_idx == 0:
                line_parts.append(f"    {header_lines[line_idx]}")
            else:
                line_parts.append(header_lines[line_idx])
            if col_idx < len(headers) - 1:
                line_parts.append(" " * MAIN_MENU_COLUMNS_SPACING)
        print("".join(line_parts))
    print(f"{RESET}")
    
    # Find maximum number of items
    max_items = max(len(items) for _, items in columns) if columns else 0
    
    # Print items side by side
    for item_idx in range(max_items):
        line_parts = []
        for col_idx, (_, items) in enumerate(columns):
            column_width = column_widths[col_idx]
            
            if item_idx < len(items):
                left_text, right_text = items[item_idx]
                left_display_width = mm.get_display_width(left_text)
                right_display_width = mm.get_display_width(right_text)
                
                # Number of dots for padding: total width - left text - right text
                dots_count = column_width - left_display_width - right_display_width
                dots = f"{DIM}{'.' * max(0, dots_count)}{RESET}"
                
                if col_idx == 0:
                    column_content = f"    {BOLD}{left_text}{RESET}{dots}{DIM}{right_text}{RESET}"
                else:
                    column_content = f"{BOLD}{left_text}{RESET}{dots}{DIM}{right_text}{RESET}"
            else:
                # Empty column if it has fewer items
                if col_idx == 0:
                    column_content = "    " + " " * column_width
                else:
                    column_content = " " * column_width
            
            line_parts.append(column_content)
            if col_idx < len(columns) - 1:
                line_parts.append(" " * MAIN_MENU_COLUMNS_SPACING)
        
        print("".join(line_parts))
        
        # Empty line after each item
        if item_idx < max_items - 1:
            print()

def _calculate_column_width(header_text, items):
    # Header width: '║' + ' ' + text + ' ' + '║'
    header_width = mm.get_display_width("║") + 1 + mm.get_display_width(header_text) + 1 + mm.get_display_width("║")
    
    # Width of the longest item
    max_item_width = 0
    for left_text, right_text in items:
        # command + 3 dots + #xx
        item_width = mm.get_display_width(left_text) + 3 + mm.get_display_width(right_text)
        max_item_width = max(max_item_width, item_width)
    
    # Required width is the maximum of header and items
    needed_width = max(header_width, max_item_width)
    
    global MAIN_MENU_COLUMN_WIDTH
    # Validate config value -- default = -1 -> letting the program use minimal calculated width if something wrong with config value
    MAIN_MENU_COLUMN_WIDTH = _validate_config_value(value=MAIN_MENU_COLUMN_WIDTH, default=-1)

    # If it fits within config width, use config width
    if MAIN_MENU_COLUMN_WIDTH < needed_width:
        value = needed_width
    else:
        value = MAIN_MENU_COLUMN_WIDTH

    # Header text width and final width must have the same parity for good appearance
    return _ensure_same_parity(value, mm.get_display_width(header_text))


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
    
    _draw_header_with_menu_options(header_text, items, add_spacing=True)
    print()

def _draw_header_with_menu_options(header_text, items, add_spacing=False) -> None:
    # Calculate final width
    # Header width: '║' + ' ' + text + ' ' + '║'
    header_width = mm.get_display_width("║") + 1 + mm.get_display_width(header_text) + 1 + mm.get_display_width("║")
    
    # Width of the longest item
    max_item_width = 0
    for left_text, right_text in items:
        # command + 3 dots + #xx
        item_width = mm.get_display_width(left_text) + 3 + mm.get_display_width(right_text)
        max_item_width = max(max_item_width, item_width)
    
    # Required width is the maximum of header and items
    needed_width = max(header_width, max_item_width)
    
    global COMMANDS_ARGUMENTS_MENU_WIDTH
    # Validate config value
    COMMANDS_ARGUMENTS_MENU_WIDTH = _validate_config_value(value=COMMANDS_ARGUMENTS_MENU_WIDTH, default=-1)

    # If it fits within config width, use config width
    if COMMANDS_ARGUMENTS_MENU_WIDTH < needed_width:
        final_width = needed_width
    else:
        final_width = COMMANDS_ARGUMENTS_MENU_WIDTH
    
    # Header text width and final width must have the same parity for good appearance
    final_width = _ensure_same_parity(final_width, mm.get_display_width(header_text))
    
    # Create header
    # Minus left and right corners
    border = "═" * (final_width - 2)
    
    # Number of spaces for header padding
    header_display_width = mm.get_display_width("║") + 1 + mm.get_display_width(header_text) + 1 + mm.get_display_width("║")
    padding_total = final_width - header_display_width
    padding_left = padding_total // 2
    padding_right = padding_total - padding_left
    
    print(f"{BOLD}")
    print(f"    ╔{border}╗")
    print(f"    ║{' ' * padding_left} {header_text} {' ' * padding_right}║")
    print(f"    ╚{border}╝")
    print(f"{RESET}")
    
    # Print items
    for i, (left_text, right_text) in enumerate(items):
        left_display_width = mm.get_display_width(left_text)
        right_display_width = mm.get_display_width(right_text)
        
        # Number of dots for padding: total width - left text - right text
        dots_count = final_width - left_display_width - right_display_width
        dots = f"{DIM}{'.' * max(0, dots_count)}{RESET}"
        
        print(f"    {BOLD}{left_text}{RESET}{dots}{DIM}{right_text}{RESET}")
        
        if add_spacing and i < len(items) - 1:
            print()


def _validate_config_value(value, default, min_value=None):
    """Validate that config value is an integer and meets minimum requirement."""
    if not vv.validate_type(variable=value, expected_type="int"):
        return default
    if min_value and value < min_value:
        return default
    return value
    
def _ensure_same_parity(width, reference_width):
    """Ensure width has the same parity (odd/even) as reference_width."""
    if width % 2 != reference_width % 2:
        return width + 1
    return width
