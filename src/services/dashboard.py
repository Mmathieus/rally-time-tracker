import config as cnfg
import utils.formatter as ff
import database.tools.state as stt
import re


VERTICAL_SPACING = cnfg.config['ui']['dashboard']['vertical_spacing']
DB_BOX_WIDTH = cnfg.config['ui']['dashboard']['db_box_width']
TABLE_BOX_WIDTH = cnfg.config['ui']['dashboard']['table_box_width']
DASHBOARD_PADDING = cnfg.config['ui']['dashboard']['padding']


###- THANKS TO Claude Sonnet 4 FOR THIS -###


def display_dashboard(
        vertical_spacing=VERTICAL_SPACING,
        db_box_width=DB_BOX_WIDTH,
        table_box_width=TABLE_BOX_WIDTH,
        dashboard_padding=DASHBOARD_PADDING,
        refresh_db_state=True
    ) -> None:

    if refresh_db_state:
        stt.capture_current_db_state()

    lines = []
    
    # Calculate total dashboard width
    total_tables_width = 2 * table_box_width + vertical_spacing
    dashboard_content_width = max(db_box_width, total_tables_width)
    dashboard_width = dashboard_content_width + 2 * dashboard_padding + 2  # +2 for left and right border
    
    # Top dashboard border
    lines.append(f"╭{'─' * (dashboard_width - 2)}╮")
    
    # Header
    header = "DASHBOARD"
    header_padding = (dashboard_width - 2 - ff.get_display_width(header)) // 2
    lines.append(f"│{' ' * header_padding}{header}{' ' * (dashboard_width - 2 - header_padding - ff.get_display_width(header))}│")
    lines.append(f"├{'─' * (dashboard_width - 2)}┤")
    
    # Empty line
    lines.append(f"│{' ' * (dashboard_width - 2)}│")
    
    # DATABASE box
    db_info = cnfg.db_state['database']
    db_name = cnfg.DB_NAME
    
    # Create database box content
    db_content = []
    db_content.append("")  # empty line under header
    
    if db_info['exists']:
        # Centered database name
        db_name_line = f"\033[32m✓\033[0m \033[1m{db_name}\033[0m"
        db_content.append(db_name_line)
        db_content.append("")  # vertical spacing
        if db_info['size'] is not None:
            db_content.append(f"Size: {_format_size(db_info['size'])}")
        
        # Add empty line at the end
        db_content.append("")
    else:
        # Centered database name
        db_name_line = f"\033[31m✗\033[0m \033[1m{db_name}\033[0m"
        db_content.append(db_name_line)
        # Add empty line at the end
        db_content.append("")
    
    # Draw database box (centered)
    db_start_pos = dashboard_padding + (dashboard_content_width - db_box_width) // 2
    
    # Top border of database box with centered DATABASE label
    db_header = "DATABASE"
    db_header_padding = (db_box_width - 2 - ff.get_display_width(db_header)) // 2
    db_header_line = f"{'─' * db_header_padding} {db_header} {'─' * (db_box_width - 2 - db_header_padding - ff.get_display_width(db_header) - 2)}"
    lines.append(f"│{' ' * (db_start_pos - 1)}┌{db_header_line}┐{' ' * (dashboard_width - db_start_pos - db_box_width - 1)}│")
    
    # Database box content
    for line in db_content:
        if line.strip():  # if not empty line
            line_clean = _strip_ansi(line)
            # Center database name
            if "\033[32m✓\033[0m" in line or "\033[31m✗\033[0m" in line:
                padding = (db_box_width - 2 - ff.get_display_width(line_clean)) // 2
                line_content = f"{' ' * padding}{line}{' ' * (db_box_width - 2 - padding - ff.get_display_width(line_clean))}"
            else:
                # Other information left-aligned with padding
                padding_left = 2
                padding_right = db_box_width - 2 - padding_left - ff.get_display_width(line_clean)
                line_content = f"{' ' * padding_left}{line}{' ' * padding_right}"
        else:
            # Empty line
            line_content = ' ' * (db_box_width - 2)
        
        lines.append(f"│{' ' * (db_start_pos - 1)}│{line_content}│{' ' * (dashboard_width - db_start_pos - db_box_width - 1)}│")
    
    # Bottom border of database box
    lines.append(f"│{' ' * (db_start_pos - 1)}└{'─' * (db_box_width - 2)}┘{' ' * (dashboard_width - db_start_pos - db_box_width - 1)}│")
    
    # Diagonal lines
    db_center = db_start_pos + db_box_width // 2
    diagonal_lines = _create_diagonal_lines(dashboard_width, dashboard_padding, dashboard_content_width, db_center, table_box_width, vertical_spacing)
    for line in diagonal_lines:
        lines.append(line)
    
    # TABLE boxes
    table_lines = _create_table_boxes(dashboard_width, dashboard_padding, dashboard_content_width, table_box_width, vertical_spacing)
    lines.extend(table_lines)
    
    # Empty line
    lines.append(f"│{' ' * (dashboard_width - 2)}│")
    
    # Bottom dashboard border
    lines.append(f"╰{'─' * (dashboard_width - 2)}╯")
    
    print(f"{'\n'.join(lines)}\n")

def _format_size(size_bytes) -> str:
    """Formats size in bytes to readable format"""
    if size_bytes is None:
        return "0"
    
    if size_bytes == 0:
        return "0"
    
    units = ['B', 'KB', 'MB', 'GB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    # Vždy zobrazí 2 desatinné miesta ak je veľkosť > 0
    return f"{size:.2f} {units[unit_index]}"

def _create_diagonal_lines(dashboard_width, dashboard_padding, dashboard_content_width, db_center, table_width, vertical_spacing) -> list:
    """Creates diagonal lines from database to tables"""
    lines = []
    
    # Calculate center positions of tables
    total_tables_width = 2 * table_width + vertical_spacing
    tables_start = dashboard_padding + (dashboard_content_width - total_tables_width) // 2
    
    left_table_center = tables_start + table_width // 2
    right_table_center = tables_start + table_width + vertical_spacing + table_width // 2
    
    # Create diagonal lines
    for i in range(vertical_spacing):
        line_content = [' '] * (dashboard_width - 2)
        
        # Left diagonal - ends in center of left table
        left_pos = db_center + int((left_table_center - db_center) * (i + 1) / vertical_spacing)
        if 0 <= left_pos < len(line_content):
            if i == vertical_spacing - 1:
                line_content[left_pos] = '▼'
            else:
                line_content[left_pos] = '╱'
        
        # Right diagonal - ends in center of right table
        right_pos = db_center + int((right_table_center - db_center) * (i + 1) / vertical_spacing)
        if 0 <= right_pos < len(line_content):
            if i == vertical_spacing - 1:
                line_content[right_pos] = '▼'
            else:
                line_content[right_pos] = '╲'
        
        lines.append(f"│{''.join(line_content)}│")
    
    return lines

def _create_table_boxes(dashboard_width, dashboard_padding, dashboard_content_width, table_width, vertical_spacing) -> list:
    """Creates boxes for tables with independent heights"""
    lines = []
    
    # Calculate table positions
    total_tables_width = 2 * table_width + vertical_spacing
    tables_start = dashboard_padding + (dashboard_content_width - total_tables_width) // 2
    
    left_table_start = tables_start
    right_table_start = tables_start + table_width + vertical_spacing
    
    # Create content for both tables
    db_exists = cnfg.db_state['database']['exists']
    left_content = _create_table_content(cnfg.db_state['timings'], cnfg.PRIMARY_TB_NAME, db_exists)
    right_content = _create_table_content(cnfg.db_state['timings_history'], cnfg.HISTORY_TB_NAME, db_exists)
    
    # Create individual table boxes
    left_box = _create_single_table_box(left_content, table_width)
    right_box = _create_single_table_box(right_content, table_width)
    
    # Get heights
    left_height = len(left_box)
    right_height = len(right_box)
    max_height = max(left_height, right_height)
    
    spacing = ' ' * vertical_spacing
    
    # Combine both boxes line by line
    for i in range(max_height):
        # Left box
        if i < left_height:
            left_part = left_box[i]
        else:
            left_part = ' ' * table_width
        
        # Right box
        if i < right_height:
            right_part = right_box[i]
        else:
            right_part = ' ' * table_width
        
        lines.append(f"│{' ' * (left_table_start - 1)}{left_part}{spacing}{right_part}{' ' * (dashboard_width - right_table_start - table_width - 1)}│")
    
    return lines

def _create_single_table_box(content, width) -> list:
    """Creates a single table box with proper borders"""
    if not content:
        return []
    
    box_lines = []
    
    # Top border with TABLE header
    table_header = "TABLE"
    table_header_padding = (width - 2 - ff.get_display_width(table_header)) // 2
    table_header_line = f"{'─' * table_header_padding} {table_header} {'─' * (width - 2 - table_header_padding - ff.get_display_width(table_header) - 2)}"
    box_lines.append(f"┌{table_header_line}┐")
    
    # Content lines
    for line in content:
        formatted_line = _format_table_line(line, width)
        box_lines.append(f"│{formatted_line}│")
    
    # Bottom border
    box_lines.append(f"└{'─' * (width - 2)}┘")
    
    return box_lines

def _create_table_content(table_info, table_name, db_exists) -> list:
    """Creates content for table with minimal height"""
    content = []
    content.append("")  # empty line under header
    
    # If database doesn't exist, table cannot exist
    table_exists = table_info['exists'] and db_exists
    
    if table_exists:
        # Centered table name
        table_name_line = f"\033[32m✓\033[0m \033[1m{table_name}\033[0m"
        content.append(table_name_line)
        content.append("")  # vertical spacing
        
        # Create label: value pairs for alignment - Order: Size, Data, Records
        info_lines = []
        if table_info.get('size') is not None:
            info_lines.append(("Size:", _format_size(table_info['size'])))
        if table_info.get('data_size') is not None:
            info_lines.append(("Data:", _format_size(table_info['data_size'])))
        if table_info.get('records') is not None:
            info_lines.append(("Records:", f"{table_info['records']:,}"))
        
        # Find longest label for alignment
        if info_lines:
            max_label_width = max(ff.get_display_width(label) for label, _ in info_lines)
            for label, value in info_lines:
                padding = max_label_width - ff.get_display_width(label)
                content.append(f"{label}{' ' * padding} {value}")
        
        # Add empty line at the end only if we have info lines
        if info_lines:
            content.append("")
    else:
        # Centered table name
        table_name_line = f"\033[31m✗\033[0m \033[1m{table_name}\033[0m"
        content.append(table_name_line)
        # Add extra empty line for non-existing tables to add spacing before bottom border
        content.append("")
    
    return content

def _format_table_line(text, width) -> str:
    """Formats line in table with proper padding"""
    if not text or not text.strip():
        return ' ' * (width - 2)
    
    text_clean = _strip_ansi(text)
    text_width = ff.get_display_width(text_clean)
    
    # Center table names (those with checkmarks/x-marks)
    if "\033[32m✓\033[0m" in text or "\033[31m✗\033[0m" in text:
        padding = (width - 2 - text_width) // 2
        return f"{' ' * padding}{text}{' ' * (width - 2 - padding - text_width)}"
    else:
        # Other information left-aligned with padding
        padding_left = 2
        padding_right = width - 2 - padding_left - text_width
        return f"{' ' * padding_left}{text}{' ' * padding_right}"

def _strip_ansi(text) -> str:
    """Removes ANSI escape codes from text"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)
