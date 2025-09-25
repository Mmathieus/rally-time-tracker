import config as cnfg

import utils.formatter as ff

import traceback
import sys
import os


###- THANKS TO Claude Sonnet 4 FOR THIS -###

def print_detailed_error(exception, use_colors=True):    
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


    # Separators
    SEP_COUNT = cnfg.config['ui']['error']['separator_count']

    top_separator = "╔" + "═" * SEP_COUNT + "╗"
    middle_separator = "╠" + "═" * SEP_COUNT + "╣"
    bottom_separator = "╚" + "═" * SEP_COUNT + "╝"
    
    print(f"\n{top_separator}")
    ff.print_colored(text=" 🚨 PROGRAM ERROR", color="RED")
    print(f"{middle_separator}\n")
    
    print(f"{ff.colorize(text='📁 File:', color='GREEN')} {filename}")
    print(f"{ff.colorize(text='📍 Line:', color='GREEN')} {line_number}")
    print(f"{ff.colorize(text='🔧 Function:', color='GREEN')} {function_name}")

    print()
    print(f"{ff.colorize(text='❌ Error type:', color='BLUE')} {exc_type}")
    print(f"{ff.colorize(text='💬 Message:', color='BLUE')} {exc_message}")

    if code_line and code_line.strip():
        print()
        ff.print_colored(text="📝 Problem code:", color="CYAN")
        print(f"   {code_line.strip()}")
    
    print()
    ff.print_colored(text="📋 Full traceback:", color="MAGENTA")
    
    # Formatted traceback
    for frame in tb:
        frame_file = os.path.basename(frame.filename)
        ff.print_colored(text=f"   📂 {frame_file}:{frame.lineno} in {frame.name}()", color="YELLOW")
        if frame.line and frame.line.strip():
            print(f"      → {frame.line.strip()}")
    
    print(f"\n{bottom_separator}\n")

# For even more compact version
def print_compact_error(exception):
    exc_info = sys.exc_info()
    tb = traceback.extract_tb(exc_info[2])
    
    if tb:
        last_frame = tb[-1]
        filename = os.path.basename(last_frame.filename)
        line_number = last_frame.lineno
        
        ff.print_colored(
            text=f"❌ {type(exception).__name__}: {exception}", 
            color="RED"
        )
        ff.print_colored(
            text=f"📍 {filename}:{line_number}", 
            color="YELLOW"
        )
        if last_frame.line:
            ff.print_colored(
                text=f"   → {last_frame.line.strip()}", 
                color="RED"
            )
    else:
        ff.print_colored(text=f"❌ {type(exception).__name__}: {exception}", color="RED")
