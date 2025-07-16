import execs
from src._config import config
from others import print_colored, upper_casing, execute_command
import re
import os
import subprocess
from queries import INSERT_GET_CURRENT_RECORD_INFO_MAIN, main_table as MT, history_table as HT


def GET_manager(searching_term):
    rally = stage = searching_term
    
    if searching_term is None:
        rally = input("🗺️ RALLY: ").strip()
        stage = input("🚥 STAGE: ").strip()
    
    execs.get(rally=upper_casing(rally), stage=upper_casing(stage), together=True if searching_term is not None else False)


def INSERT_manager(data_obtained, record):
    if not data_obtained:
        entry = input("🏁 RALLY | 🚦 STAGE | 🚗 CAR | ⏱️ TIME\n➡️ ").strip()
        if not entry:
            print_colored(text="🚫 Insert cancelled\n", color="YELLOW")
            return

        #? CHECK: Count of arguments
        record = entry.split()
        if len(record) != 4:
            print_colored(text="❌ Required number of arguments is 4\n", color="RED")
            return
    
    #? CHECK: TIME format
    time_pattern = r'^\d+:(0[0-9]|[1-5][0-9]):\d{3}$'
    if re.match(time_pattern, record[3]) is None:
        print_colored(text="❌ Invalid format of TIME\n", color="RED")
        return
    
    record[0], record[1] = map(upper_casing, record[:2])
    
    def time_convertion(time_str):
        minutes, seconds, milliseconds = map(int, time_str.split(':'))
        return (minutes * 60 * 1000) + (seconds * 1000) + milliseconds

    #? CHECK: Exists old record?
    new_time = time_convertion(time_str=record[3])
    db_record = execute_command(sql=INSERT_GET_CURRENT_RECORD_INFO_MAIN.format(STAGE=record[1]), header=False, capture=True, text=True).stdout.strip()
    db_id, db_time = (lambda info: (info[0], time_convertion(time_str=info[1])))(db_record.strip('()').split(',')) if db_record else (None, None)

    #? CHECK: Is improvement?
    improvement = None
    if db_time:
        if db_time <= new_time:
            print_colored(text="🚫 Stage time not improved\n", color="YELLOW")
            return
        
        def time_difference(ms):
                minutes = ms // (60 * 1000)
                ms %= 60 * 1000
                seconds = ms // 1000
                milliseconds = ms % 1000
                return f"{minutes}:{seconds:02}:{milliseconds:03}"
        
        improvement = print_colored(text=f"🆕 - {time_difference(db_time - new_time)}", color="MAGENTA", display=False)

    record[2] = record[2] if record[2] != '0' else "i20"
    record[3] = re.sub(r':(?!.*:)', '.', record[3])
    
    execs.insert(*record, gain=improvement, old_record_id=db_id)


def HISTORY_manager():
    while True:
        entry = input("🚥 STAGE: ").strip()
        if not entry:
            break
        execs.history(stage=upper_casing(entry))
    print_colored(text="🚫 History has ended.\n", color="YELLOW")


def ACCESS_manager(table_choice):
    if table_choice not in config['table_choice'][1:]:
        print_colored(text=f"❌ No access to {table_choice}\n", color="RED")
        return

    execs.access(table=table_choice, ids=[])
    while True:
        remove = input("ID: ").strip()
        if not remove:
            break
        ids = remove.split()
        ids[:] = [int(id) if id.isdigit() else id for id in ids]
        execs.access(table=table_choice, ids=ids)
    print_colored(text="🚫 Access has ended\n", color="YELLOW")


def CLEAR_manager(table_choice):
    clear_options = {
        #? all
        config['table_choice'][0]: {
            'queries': (MT, HT),
            'tables': config['DB_tables']
        },
        #? main
        config['table_choice'][1]: {
            'queries': (MT,),
            'tables': (config['DB_tables'][0],)
        },
        #? history
        config['table_choice'][2]: {
            'queries': (HT,),
            'tables': (config['DB_tables'][1],)
        }
    }
    
    if table_choice not in clear_options:
        print_colored(text=f"❌ No access to {table_choice}\n", color="RED")
        return

    execs.clear(queries=clear_options[table_choice]['queries'], tables=clear_options[table_choice]['tables'])


def IMPORT_manager(table_choice, file_path):
    import_options = {
        #? all
        config['table_choice'][0]: {
            'files': (config['MT_location'], config['HT_location']),
            'tables': config['DB_tables'],
            'sequences': (True, False),
        },
        #? main
        config['table_choice'][1]: {
            'files': (config['MT_location'],),
            'tables': (config['DB_tables'][0],),
            'sequences': (True,),
        },
        #? history
        config['table_choice'][2]: {
            'files': (config['HT_location'],),
            'tables': (config['DB_tables'][1],),
            'sequences': (False,),
        }
    }
    
    if file_path is None:
        if table_choice not in import_options.keys():
            print_colored(text=f"❌ No access to {table_choice}\n", color="RED")
            return
        
        def validate_files(file_paths):
                missing_files = [path for path in file_paths if not os.path.exists(path)]
                return False if missing_files else True

        if not validate_files(import_options[table_choice]['files']):
            print_colored(text="❌ File(s) not found\n", color="RED")
            return

        print_colored(text="✅ File(s) found\n✅ Importing according to config", color="GREEN")
        execs.csv_import(files=import_options[table_choice]['files'],
                         tables=import_options[table_choice]['tables'],
                         sequences=import_options[table_choice]['sequences'])
        return
    
    if os.path.exists(file_path) and (table_choice in list(import_options.keys())[1:]):
        print_colored(text="✅ File and table found", color="GREEN")
        execs.csv_import(files=[file_path],
                         tables=import_options[table_choice]['tables'],
                         sequences=import_options[table_choice]['sequences'])
    else:
        print_colored(text="❌ Wrong file path\n", color="RED")


def UPLAOD_manager(choice, message):
    if message is None:
        message = input("📝 Commit message: ").strip()
        if not message:
            print_colored(text="🚫 Upload cancelled\n", color="YELLOW")
            return
    
    options = {
        config["table_choice"][0]: {
            "add": 'git add . && git commit -m "{msg}" && git push',
            "status": "git status"
        },
        'code': {
            "add": 'git add :!data/ && git commit -m "{msg}" && git push',
            "status": 'git status :!data/'
        },
        'data': {
            "add": 'git add data/ && git commit -m "{msg}" && git push',
            "status": 'git status data/'
        }
    }

    if choice not in options:
        print_colored(text=f"❌ No option '{choice}'\n", color="RED")
        return
    
    if choice in (config["table_choice"][0], "data"):
        execs.csv_export(choice=config["table_choice"][0])
    
    
    
    status = subprocess.run(args=options[choice]["status"], shell=True, check=True, capture_output=True, text=True)
    if "nothing to commit" in status.stdout:
        print_colored(text="⚠️ No changes to commit\n", color="YELLOW")
        return
    
    execs.uplaod_all(cmd=options[choice]["add"].format(msg=message))

