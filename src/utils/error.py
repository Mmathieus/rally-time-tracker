import config as cnfg

import utils.formatter as ff

import traceback
import sys
import os


###- THANKS TO Claude Sonnet 4 FOR THIS -###


def print_detailed_error(exception):    
    # Get error information
    exc_type = type(exception).__name__
    exc_message = str(exception)
    
    # Get traceback information
    exc_info = sys.exc_info()
    tb = traceback.extract_tb(exc_info[2])
    
    if tb:
        # Last frame (where the error actually occurred)
        last_frame = tb[-1]
        filename = os.path.basename(last_frame.filename)  # Only filename
        line_number = last_frame.lineno
        function_name = last_frame.name
        code_line = last_frame.line
    else:
        filename = "unknown"
        line_number = "unknown"
        function_name = "unknown"
        code_line = "unknown"

    # Border characters - defined in one place
    BORDER_VERTICAL = "║"
    BORDER_TOP_LEFT = "╔"
    BORDER_TOP_RIGHT = "╗"
    BORDER_BOTTOM_LEFT = "╚"
    BORDER_BOTTOM_RIGHT = "╝"
    BORDER_HORIZONTAL_TOP = "═"
    BORDER_HORIZONTAL_BOTTOM = "═"
    BORDER_MIDDLE_LEFT = "╟"
    BORDER_MIDDLE_RIGHT = "╢"
    BORDER_HORIZONTAL_MIDDLE = "─"

    # Helper function for italic
    def italic(text):
        return f"{ff.formats['ITALIC']}{text}{ff.colors['RESET']}"
    
    # Helper function for italic + color
    def italic_colorize(text, color):
        return f"{ff.formats['ITALIC']}{ff.colors[color]}{text}{ff.colors['RESET']}"
    
    # Helper function for normal colorize (without italic)
    def colorize(text, color):
        return f"{ff.colors[color]}{text}{ff.colors['RESET']}"
    
    # Calculate alignment for GROUP 1 (FILE, LINE, FUNCTION)
    group1_labels = ["📄 FILE", "📍 LINE", "🔧 FUNCTION"]
    max_label1_width = max([ff.get_display_width(label) for label in group1_labels])
    
    # Calculate width of entire group 1
    group1_lines = [
        f" 📄 FILE" + " " * (max_label1_width - ff.get_display_width("📄 FILE")) + f" : {filename}",
        f" 📍 LINE" + " " * (max_label1_width - ff.get_display_width("📍 LINE")) + f" : {line_number}",
        f" 🔧 FUNCTION" + " " * (max_label1_width - ff.get_display_width("🔧 FUNCTION")) + f" : {function_name}"
    ]
    max_group1_width = max([ff.get_display_width(line) for line in group1_lines])
    
    # Calculate alignment for GROUP 2 (ERROR TYPE, REASON)
    group2_labels = ["⚠️ ERROR TYPE", "❓ REASON"]
    max_label2_width = max([ff.get_display_width(label) for label in group2_labels])
    
    # Calculate width of entire group 2 (only ERROR TYPE and REASON)
    group2_lines = [
        f" ⚠️ ERROR TYPE" + " " * (max_label2_width - ff.get_display_width("⚠️ ERROR TYPE")) + f" : {exc_type}",
        f" ❓ REASON" + " " * (max_label2_width - ff.get_display_width("❓ REASON")) + f" : {exc_message}"
    ]
    max_group2_width = max([ff.get_display_width(line) for line in group2_lines])
    
    # If PROBLEM CODE exists, it's a separate group 3
    has_problem_code = code_line and code_line.strip()
    if has_problem_code:
        problem_line = f" 🎯 PROBLEM CODE : {code_line.strip()}"
        max_group3_width = ff.get_display_width(problem_line)
    
    # Calculate alignment for GROUP 4 (TRACEBACK) - find longest prefix before →
    max_traceback_prefix_width = 0
    for frame in tb:
        frame_file = os.path.basename(frame.filename)
        prefix = f"    📄 {frame_file} on line {frame.lineno} in {frame.name}()"
        prefix_width = ff.get_display_width(prefix)
        if prefix_width > max_traceback_prefix_width:
            max_traceback_prefix_width = prefix_width

    # Collect all lines to measure total width
    lines_to_measure = []
    lines_to_measure.append("║ 🚨 PROGRAM ERROR")
    lines_to_measure.append("║")
    
    # Group 1
    for line in group1_lines:
        lines_to_measure.append(f"║{line}")
    
    lines_to_measure.append("║")
    
    # Group 2
    for line in group2_lines:
        lines_to_measure.append(f"║{line}")
    
    if has_problem_code:
        lines_to_measure.append("║")
        lines_to_measure.append(f"║ 🎯 PROBLEM CODE : {code_line.strip()}")
    
    lines_to_measure.append("║")
    lines_to_measure.append("║ 🗂️ FULL TRACEBACK:")
    
    # Group 4 - Traceback
    for frame in tb:
        frame_file = os.path.basename(frame.filename)
        prefix = f"║    📄 {frame_file} on line {frame.lineno} in {frame.name}()"
        prefix_clean = f"    📄 {frame_file} on line {frame.lineno} in {frame.name}()"
        
        if frame.line and frame.line.strip():
            padding = max_traceback_prefix_width - ff.get_display_width(prefix_clean)
            full_line = prefix + " " * padding + f" → {frame.line.strip()}"
            lines_to_measure.append(full_line)
        else:
            lines_to_measure.append(prefix)
        
        lines_to_measure.append("║")
    
    # Calculate max width
    max_width = 0
    for line in lines_to_measure:
        width = ff.get_display_width(line)
        if width > max_width:
            max_width = width
    
    # SEP_COUNT is the content width without `║` characters
    SEP_COUNT = max_width - 1
    
    # Create separators
    top_separator = BORDER_TOP_LEFT + BORDER_HORIZONTAL_TOP * SEP_COUNT + BORDER_TOP_RIGHT
    middle_separator = BORDER_MIDDLE_LEFT + BORDER_HORIZONTAL_MIDDLE * SEP_COUNT + BORDER_MIDDLE_RIGHT
    bottom_separator = BORDER_BOTTOM_LEFT + BORDER_HORIZONTAL_BOTTOM * SEP_COUNT + BORDER_BOTTOM_RIGHT
    
    # Create group separators (according to group width)
    def create_group_separator(group_width):
        horizontal = BORDER_HORIZONTAL_MIDDLE * group_width
        padding = " " * (SEP_COUNT - group_width)
        return BORDER_MIDDLE_LEFT + horizontal + padding + BORDER_MIDDLE_RIGHT
    
    # Helper function to print line with borders
    def print_bordered_line(content, content_display_width):
        padding = SEP_COUNT - content_display_width
        print(f"{BORDER_VERTICAL}{content}" + " " * padding + BORDER_VERTICAL)
    
    # Now print everything with border
    print(f"\n{top_separator}")
    
    content = f" {italic_colorize('🚨 PROGRAM ERROR', 'RED')}"
    print_bordered_line(content, ff.get_display_width(" 🚨 PROGRAM ERROR"))
    
    print(f"{middle_separator}")
    print_bordered_line("", 0)
    
    # GROUP 1 - aligned
    label1 = f" 📄 {italic('FILE')}"
    padding1 = max_label1_width - ff.get_display_width("📄 FILE")
    content = label1 + " " * padding1 + f" : {filename}"
    print_bordered_line(content, ff.get_display_width(f" 📄 FILE" + " " * padding1 + f" : {filename}"))
    
    label2 = f" 📍 {italic('LINE')}"
    padding2 = max_label1_width - ff.get_display_width("📍 LINE")
    content = label2 + " " * padding2 + f" : {line_number}"
    print_bordered_line(content, ff.get_display_width(f" 📍 LINE" + " " * padding2 + f" : {line_number}"))
    
    label3 = f" 🔧 {italic('FUNCTION')}"
    padding3 = max_label1_width - ff.get_display_width("🔧 FUNCTION")
    content = label3 + " " * padding3 + f" : {function_name}"
    print_bordered_line(content, ff.get_display_width(f" 🔧 FUNCTION" + " " * padding3 + f" : {function_name}"))

    # Separator for group 1
    print(create_group_separator(max_group1_width))
    print_bordered_line("", 0)
    
    # GROUP 2 - aligned
    label4 = f" ⚠️ {italic('ERROR TYPE')}"
    padding4 = max_label2_width - ff.get_display_width("⚠️ ERROR TYPE")
    content = label4 + " " * padding4 + f" : {exc_type}"
    print_bordered_line(content, ff.get_display_width(f" ⚠️ ERROR TYPE" + " " * padding4 + f" : {exc_type}"))
    
    label5 = f" ❓ {italic('REASON')}"
    padding5 = max_label2_width - ff.get_display_width("❓ REASON")
    content = label5 + " " * padding5 + f" : {exc_message}"
    print_bordered_line(content, ff.get_display_width(f" ❓ REASON" + " " * padding5 + f" : {exc_message}"))

    # Separator for group 2
    print(create_group_separator(max_group2_width))

    if has_problem_code:
        print_bordered_line("", 0)
        content = f" 🎯 {italic('PROBLEM CODE')} : {code_line.strip()}"
        print_bordered_line(content, ff.get_display_width(f" 🎯 PROBLEM CODE : {code_line.strip()}"))
        
        # Separator for group 3 (PROBLEM CODE)
        print(create_group_separator(max_group3_width))
    
    print_bordered_line("", 0)
    
    content = f" {italic('🗂️ FULL TRACEBACK:')}"
    print_bordered_line(content, ff.get_display_width(" 🗂️ FULL TRACEBACK:"))
    
    # GROUP 4 - Traceback aligned (without italic on line and function)
    for frame in tb:
        frame_file = os.path.basename(frame.filename)

        file_part = f"📄 {ff.colorize(text=frame_file, color="GREEN")}"
        
        #file_part = f"📄 {frame_file}"
        line_part = ff.colorize(text=f"line {frame.lineno}", color='YELLOW')
        func_part = ff.colorize(text=f"{frame.name}()", color='CYAN')
        
        prefix_display = f"    {file_part} on line {frame.lineno} in {frame.name}()"
        prefix_colored = f"    {file_part} on {line_part} in {func_part}"
        
        if frame.line and frame.line.strip():
            padding = max_traceback_prefix_width - ff.get_display_width(prefix_display)
            code_part = f" → {frame.line.strip()}"
            content = prefix_colored + " " * padding + code_part
            display_width = ff.get_display_width(prefix_display + " " * padding + code_part)
            print_bordered_line(content, display_width)
        else:
            content = prefix_colored
            print_bordered_line(content, ff.get_display_width(prefix_display))
        
        print_bordered_line("", 0)
    
    print(f"{bottom_separator}\n")

# For even more compact version
def print_compact_error(exception):
    exc_info = sys.exc_info()
    tb = traceback.extract_tb(exc_info[2])
    
    if tb:
        last_frame = tb[-1]
        filename = os.path.basename(last_frame.filename)
        line_number = last_frame.lineno
        
        ff.print_colored(
            text=f"⚠️ {type(exception).__name__}: {exception}", 
            color="RED"
        )
        ff.print_colored(
            text=f"📄 {filename}:{line_number}", 
            color="YELLOW"
        )
        if last_frame.line:
            ff.print_colored(
                text=f"   → {last_frame.line.strip()}", 
                color="RED"
            )
    else:
        ff.print_colored(text=f"⚠️ {type(exception).__name__}: {exception}", color="RED")
