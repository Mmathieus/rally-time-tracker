from traceback import extract_tb
from src._config import config
import subprocess
from pprint import pprint


colors = {
    "RED" : "\033[31m",
    "CYAN" : "\033[36m",
    "GREEN" : "\033[32m",
    "YELLOW" : "\033[33m",
    "MAGENTA" : "\033[35m",
    "RESET" : "\033[0m"
}


def print_colored(text, color, display=True):
    if not display:
        return f"{colors[color]}{text}{colors['RESET']}"
    print(f"{colors[color]}{text}{colors['RESET']}")


def error_info(error):
    tb = extract_tb(error.__traceback__)
    filename, line_num, _, _ = tb[-1]
    print_colored(text=f"ERROR: {error}", color="RED")
    print_colored(text=f"File: {filename}", color="CYAN")
    print_colored(text=f"Line: {line_num}\n", color="YELLOW")


def upper_casing(string):
    string = string.strip()
    return '-'.join([word.capitalize() for word in string.split('-')])


def execute_command(sql, pager=False, header=True, capture=False, text=False):
    command = f"psql -U {config['usrnm']} -d {config['db']}"
    if pager: command += " -P pager=off"
    if not header: command += " -t"
    if sql is not None: command += f" -c \"{sql}\""
    return subprocess.run(args=command, shell=True, check=True, capture_output=capture, text=text)


class Tracker:
    main_records = { }
    history_records = {
        "added" : { },
        "removed" : { }
    }

    @classmethod
    def add_record(cls, stage, time):
        if stage in cls.main_records:
            if cls.main_records[stage][1] == 'A':
                cls.main_records[stage] = (time, 'A')
            else:
                if time == cls.main_records[stage][0]:
                    del cls.main_records[stage]
                else:
                    cls.main_records[stage] = (time, 'A')
        else:
            cls.main_records[stage] = (time, 'A')
        
        if stage not in cls.history_records["added"]:
            cls.history_records["added"][stage] = []
        cls.history_records["added"][stage].append(time)

    @classmethod
    def remove_record(cls, where, stage, time):
        if where == 'M':
            if stage in cls.main_records:
                del cls.main_records[stage]
            else:
                cls.main_records[stage] = (time, 'R')
        else:
            if stage not in cls.history_records["removed"]:
                cls.history_records["removed"][stage] = []
            cls.history_records["removed"][stage].append(time)
    
    @classmethod
    def status(cls, what):
        if what == 'M':
            return True if cls.main_records else False
        else:
            if cls.history_records["added"].keys() != cls.history_records["removed"].keys():
                return True
            
            for stage in cls.history_records["added"]:
                idx = 0
                while idx != len(cls.history_records["added"][stage]):
                    time = cls.history_records["added"][stage][idx]
                    if time in cls.history_records["removed"][stage]:
                        cls.history_records["added"][stage].remove(time)
                        cls.history_records["removed"][stage].remove(time)
                    else:
                        idx += 1
                
                if cls.history_records["added"][stage] != [] or cls.history_records["removed"][stage] != []:
                    return True
                
            return False
    
    @classmethod
    def reset(cls, what='MH'):
        if 'M' in what:
            cls.main_records.clear()
        if 'H' in what:
            cls.history_records["added"].clear()
            cls.history_records["removed"].clear()

    @classmethod
    def look(cls):
        pprint(cls.main_records)
        print()
        pprint(cls.history_records)
        