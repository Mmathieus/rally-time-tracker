import config as cnfg
import utils.other as u_othr
import database.tools.state as stt


VERTICAL_SPACING = cnfg.config['ui']['dashboard']['vertical_spacing']
DASHBOARD_PADDING = cnfg.config['ui']['dashboard']['padding']

CHECK = "\033[32m✓\033[0m"
CROSS = "\033[31m✗\033[0m"


###- THANKS TO Claude Opus 4.8 FOR THIS -###


def display_dashboard(vertical_spacing=VERTICAL_SPACING, dashboard_padding=DASHBOARD_PADDING, refresh_db_state=True) -> None:
    if refresh_db_state:
        stt.capture_current_db_state()

    DB_EXISTS = cnfg.db_state['database']['exists']

    db_box = _build_db_box(info=cnfg.db_state['database'])
    left_box = _build_table_box(info=cnfg.db_state['timings'], name=cnfg.PRIMARY_TB_NAME, db_exists=DB_EXISTS)
    right_box = _build_table_box(info=cnfg.db_state['timings_history'], name=cnfg.HISTORY_TB_NAME, db_exists=DB_EXISTS)

    # Every box sizes itself to its content -> widths are read back from the finished boxes
    db_width = u_othr.get_display_width(db_box[0])
    left_width = u_othr.get_display_width(left_box[0])
    right_width = u_othr.get_display_width(right_box[0])

    tables_width = left_width + vertical_spacing + right_width
    dashboard_content_width = max(db_width, tables_width)
    dashboard_width = dashboard_content_width + 2 * dashboard_padding + 2  # +2 for left and right border

    # Starting columns (column 0 = dashboard's left border), both groups centered
    db_start = 1 + dashboard_padding + (dashboard_content_width - db_width) // 2
    tables_start = 1 + dashboard_padding + (dashboard_content_width - tables_width) // 2

    # Columns the ┬ / ▼ connectors sit on
    db_connector = db_start + db_width // 2
    left_connector = tables_start + left_width // 2
    right_connector = tables_start + left_width + vertical_spacing + right_width // 2

    lines = [_dashboard_top_border(dashboard_width=dashboard_width)]

    # DATABASE box
    for line in db_box:
        lines.append(_frame(content=line, start=db_start, dashboard_width=dashboard_width))

    # Branches leading from DATABASE down to both TABLES
    branch = _branch_line(left=left_connector, right=right_connector, middle=db_connector)
    lines.append(_frame(content=branch, start=left_connector, dashboard_width=dashboard_width))
    lines.append(_frame(content=_arrows_line(left=left_connector, right=right_connector), start=left_connector, dashboard_width=dashboard_width))

    # TABLE boxes side by side
    for line in _merge_boxes(left_box=left_box, right_box=right_box, left_width=left_width, right_width=right_width, spacing=vertical_spacing):
        lines.append(_frame(content=line, start=tables_start, dashboard_width=dashboard_width))

    lines.append(f"╰{'─' * (dashboard_width - 2)}╯")

    print(f"{'\n'.join(lines)}\n")


# --- BOXES ---

def _build_db_box(info) -> list[str]:
    SIZE = _format_size(info['size']) if info['exists'] and info['size'] is not None else ""

    inner_width = max(len(SIZE), _name_width(name=cnfg.DB_NAME)) + 2

    box = [_box_header(name=cnfg.DB_NAME, exists=info['exists'], inner_width=inner_width)]

    # Size only if DATABASE EXISTS
    if SIZE:
        box.append(f"│{SIZE.center(inner_width)}│")

    # Bottom border carries the connector down to the TABLE boxes
    left_dashes = (inner_width + 2) // 2 - 1
    box.append(f"└{'─' * left_dashes}┬{'─' * (inner_width - 1 - left_dashes)}┘")

    return box

def _build_table_box(info, name, db_exists) -> list[str]:
    # DATABASE doesn't exist -> TABLE cannot exist either
    EXISTS = bool(info['exists']) and db_exists

    # Info only if TABLE EXISTS
    rows = []
    if EXISTS:
        if info['size'] is not None:
            rows.append(("Size:", _format_size(info['size'])))
        if info['data_size'] is not None:
            rows.append(("Data:", _format_size(info['data_size'])))
        if info['records'] is not None:
            rows.append(("Records:", f"{info['records']:,}"))

    # Widest 'label + value' pair decides the width, but the name in the header can be wider
    rows_width = max((len(label) + 2 + len(value) for label, value in rows), default=0)
    inner_width = max(rows_width, _name_width(name=name)) + 2

    box = [_box_header(name=name, exists=EXISTS, inner_width=inner_width)]

    # Label left-aligned, value right-aligned
    for label, value in rows:
        box.append(f"│ {label}{value.rjust(inner_width - 2 - len(label))} │")

    box.append(f"└{'─' * inner_width}┘")

    return box

# Top border with the name sitting inside it
def _box_header(name, exists, inner_width) -> str:
    label = f" {CHECK if exists else CROSS} \033[1m{name}\033[0m "

    dashes = inner_width - u_othr.get_display_width(label)
    left_dashes = dashes // 2

    return f"┌{'─' * left_dashes}{label}{'─' * (dashes - left_dashes)}┐"

# ' <mark> <name> ' -> the mark plus the 3 spaces around it
def _name_width(name) -> int:
    return u_othr.get_display_width(name) + 4


# --- LAYOUT ---

def _dashboard_top_border(dashboard_width) -> str:
    TITLE = " DASHBOARD "

    dashes = dashboard_width - 2 - len(TITLE)
    left_dashes = dashes // 2

    return f"╭{'─' * left_dashes}{TITLE}{'─' * (dashes - left_dashes)}╮"

# Puts a line between the dashboard borders, starting at the given column
def _frame(content, start, dashboard_width) -> str:
    filler = dashboard_width - 1 - start - u_othr.get_display_width(content)
    return f"│{' ' * (start - 1)}{content}{' ' * filler}│"

def _branch_line(left, right, middle) -> str:
    # DATABASE points down somewhere between both TABLES -> ┴ joins it
    if left < middle < right:
        return f"┌{'─' * (middle - left - 1)}┴{'─' * (right - middle - 1)}┐"
    return f"┌{'─' * (right - left - 1)}┐"

def _arrows_line(left, right) -> str:
    return f"▼{' ' * (right - left - 1)}▼"

# Both boxes side by side, the shorter one padded to the taller one's height
def _merge_boxes(left_box, right_box, left_width, right_width, spacing) -> list[str]:
    lines = []

    for i in range(max(len(left_box), len(right_box))):
        left_line = left_box[i] if i < len(left_box) else ' ' * left_width
        right_line = right_box[i] if i < len(right_box) else ' ' * right_width
        lines.append(f"{left_line}{' ' * spacing}{right_line}")

    return lines


def _format_size(size_bytes) -> str:
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
