import utils.formatter as ff
from pathlib import Path
import subprocess


def json_settings_exec() -> None:
    # Path to config.json - 2 levels up from /src/services/
    config_path = Path(__file__).parent.parent.parent / 'config.json'
    
    # Check if file exists
    if not config_path.exists():
        ff.print_colored(text="CONFIG FILE 'config.json' NOT FOUND IN PROJET ROOT\n", color="RED")
        return
    
    ff.print_colored(text="OPENING EDITOR...\nCLOSE EDITOR TO CONTINUE.\n", color="GREEN")
    
    try:
        subprocess.run(['notepad.exe', str(config_path)])
        ff.print_colored(text="NEW CHANGES TAKE EFFECT AFTER PROGRAM RESTART.\n", color="GREEN")
    except Exception as e:
        ff.print_colored(text="PROBLEM OPENING EDITOR\n", color="RED")
