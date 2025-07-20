from config import config
import utils.inputter as ii
import utils.formatter as ff
import utils.menu as mm
import database.others.executor as exe

from pathlib import Path
import tkinter as tk
from tkinter import filedialog

# IMPORT main
# IMPORT main "C:..."   | exists, is_csv, is_file
# IMPORT main gui
# IMPORT main default

## Funkcia na overenie suboru

## Vlastna funckia pre GUI, Path a Default
## samostatny exec pre GUI a Default, manager a exec pre Path 


TIMINGS_ALIAS = config['table_references']['timings']
TIMINGS_HISTORY_ALIAS = config['table_references']['timings_history']

TABLE_OPTIONS = (TIMINGS_ALIAS, TIMINGS_HISTORY_ALIAS)

FILE_SELECTION_OPTIONS = ("path", "gui", "default")

def _import_manager(table, file_selection=None):
    if table not in TABLE_OPTIONS:
        # ff.print_colored(text=f"INVALID TABLE '{table}'.\n", color="YELLOW")
        return

    if not file_selection:
        mm.display_menu(title="FILE OPTIONS", options=tuple(opt.capitalize() for opt in FILE_SELECTION_OPTIONS))
        file_selection = ii.get_user_input()
    
    if file_selection not in FILE_SELECTION_OPTIONS:
        # ff.print_colored(text=f"INVALID CHOICE '{selection_choice}'.\n", color="YELLOW")
        return
    

    if file_selection == "gui":
        root = tk.Tk()
        root.withdraw()
        
        file_path = filedialog.askopenfilename(
            title="Select a CSV file",
            filetypes=[("CSV files", "*.csv")]
        )
        
        root.destroy()
        
        if not file_path:
            return
        
        FilePath = Path(file_path)

        IMPORT_TIMINGS_QUERY = f"\\copy timings FROM '{FilePath}' WITH (FORMAT csv);"
        IMPORT_TIMINGS_HISTORY_QUERY = f"\\copy timings_history FROM '{FilePath}' WITH (FORMAT csv);"

        if table == TIMINGS_ALIAS:
            answer = exe.execute_query(sql=IMPORT_TIMINGS_QUERY, header=False, capture=True)
        else:
            answer = exe.execute_query(sql=IMPORT_TIMINGS_HISTORY_QUERY, header=False, capture=True)
        
        print(answer)
        ff.print_colored(text="IMPORT INTO (table_name) SUCCESFUL.\n", color="GREEN")
    
    else:
        if file_selection == "path":
            file_path = ii.get_user_input(prompt="Enter full path to .csv file", lowercase=False).replace('"', '').replace("'", '')
            FilePath = Path(file_path)

            if not FilePath.exists() or not FilePath.is_file() or FilePath.suffix.lower() != '.csv':
                return

            IMPORT_TIMINGS_QUERY = f"\\copy timings FROM '{FilePath}' WITH (FORMAT csv);"
            IMPORT_TIMINGS_HISTORY_QUERY = f"\\copy timings_history FROM '{FilePath}' WITH (FORMAT csv);"

            if table == TIMINGS_ALIAS:
                answer = exe.execute_query(sql=IMPORT_TIMINGS_QUERY, header=False, capture=True)
            else:
                answer = exe.execute_query(sql=IMPORT_TIMINGS_HISTORY_QUERY, header=False, capture=True)
            
            print(answer)
            ff.print_colored(text="IMPORT INTO (table_name) SUCCESFUL.\n", color="GREEN")
        
        if file_selection == "default":
            if table == TIMINGS_ALIAS:
                FilePath = Path(config['default_import_locations']['timings'])
            else:
                FilePath = Path(config['default_import_locations']['timings_history'])
            
            if not FilePath.exists() or not FilePath.is_file() or FilePath.suffix.lower() != '.csv':
                return

            IMPORT_TIMINGS_QUERY = f"\\copy timings FROM '{FilePath}' WITH (FORMAT csv);"
            IMPORT_TIMINGS_HISTORY_QUERY = f"\\copy timings_history FROM '{FilePath}' WITH (FORMAT csv);"

            if table == TIMINGS_ALIAS:
                answer = exe.execute_query(sql=IMPORT_TIMINGS_QUERY, header=False, capture=True)
            else:
                answer = exe.execute_query(sql=IMPORT_TIMINGS_HISTORY_QUERY, header=False, capture=True)
            
            print(answer)
            ff.print_colored(text="IMPORT INTO (table_name) SUCCESFUL.\n", color="GREEN")


            

