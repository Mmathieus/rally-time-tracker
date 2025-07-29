from src._config import config
from others import *
import queries
import subprocess
import sys
from queries import (SPECIAL_RETRIEVE_MAIN, SPECIAL_DELETE_CURRENT_RECORD_MAIN,
                     SPECIAL_RETRIEVE_HISTORY, SPECIAL_DELETE_CURRENT_RECORD_HISTORY)


def get(rally, stage, together=False):
    try:
        gtinf = queries.GET_RETRIEVE_MAIN

        if together:
            gtinf = (queries.GET_SPECIAL_RETRIEVE_MAIN + queries.GET_FORMAT_MAIN).format(RALLY=rally, STAGE=stage)
        else:
            conditions = []
            if rally: conditions.append(f" rally = '{rally}' ")
            if stage: conditions.append(f" stage = '{stage}' ")

            if conditions != []:
                gtinf += f" WHERE {' AND '.join(conditions)}"

            gtinf += queries.GET_FORMAT_MAIN

        print()
        execute_command(sql=gtinf, pager=True)

    except Exception as e:
        error_info(e)


def insert(rally, stage, car, time, gain, old_record_id):
    try:

        execute_command(sql=queries.INSERT_INTO_MAIN_AND_HISTORY.format(RALLY=rally, STAGE=stage, CAR=car, TIME=time), capture=True)
        print_colored(text="\n✅ NEW record added", color="GREEN")
        print_colored(text="✅ NEW record added to history table", color="GREEN")
        
        Tracker.add_record(stage=stage, time=time.replace('.', ':'))

        if gain is not None:
            execute_command(sql=queries.SPECIAL_DELETE_CURRENT_RECORD_MAIN.format(ID=old_record_id), capture=True)
            print_colored(text="✅ OLD record deleted", color="YELLOW")
            print(gain)

        get(rally, stage)

    except Exception as e:
        error_info(e)


def history(stage):
    try:
        query = queries.HISTORY_RETRIEVE_HISTORY_SPECIFIC.format(stage)
        if stage == '.':
            query = queries.HISTORY_RETRIEVE_HISTORY_ALL

        print()
        execute_command(sql=query, pager=True)
    
    except Exception as e:
        error_info(e)


def access(table, ids, look=True):
    try:

        access_options = {
            #? main
            config['table_choice'][1]: {
                'records': SPECIAL_RETRIEVE_MAIN,
                'deletion': SPECIAL_DELETE_CURRENT_RECORD_MAIN
            },
            #? history
            config['table_choice'][2]: {
                'records': SPECIAL_RETRIEVE_HISTORY,
                'deletion': SPECIAL_DELETE_CURRENT_RECORD_HISTORY
            }
        }

        outcome = []
        for id in ids:
            if not isinstance(id, int):
                outcome.append(print_colored(text=f"⚠️ Skipping record '{id}' - invalid", color="YELLOW", display=False))
                continue
            
            result = execute_command(sql=access_options[table]['deletion'].format(ID=id), header=False, capture=True, text=True).stdout.strip().split()
        
            if result[-1] == '0':
                outcome.append(print_colored(text=f"❌ Record {id} not found", color="RED", display=False))
                continue
            
            outcome.append(print_colored(text=f"✅ Record {id} deleted", color="GREEN", display=False))

            def format_time(time_str):
                _, minutes, rest = time_str.split(':')
                seconds, milliseconds = rest.split('.')

                minutes = int(minutes)
                milliseconds = milliseconds.ljust(3, '0')
                return f"{minutes}:{seconds}:{milliseconds}"

            Tracker.remove_record(where=table[0].upper(), stage=result[0], time=format_time(result[2]))
        
        #? Openning look
        if look and ids == []:
            print()
            execute_command(sql=access_options[table]['records'], pager=True)
            return
        #? Show updated records after at least 1 removal
        if look and id != [] and any("deleted" in status for status in outcome):
            print()
            execute_command(sql=access_options[table]['records'], pager=True)
        
        for status in outcome:
            print(status)
        print() if not look else None

    except Exception as e:
        error_info(e)


def program_reset():
    try:
        csv_export(choice=config["table_choice"][0])
        
        print_colored(text="🔄 Restarting program ...\n", color="YELLOW")
        subprocess.run(args=["powershell.exe", "-ExecutionPolicy", "Bypass", "-Command", "python -u code/main.py"], check=True)
        sys.exit()
    
    except Exception as e:
        error_info(e)


def clear(queries, tables):
    try:
        for query, table in zip(queries, tables):
            try:
                execute_command(sql=query, capture=True)
                print_colored(text=f"✅ Table {table} REFRESHED", color="GREEN")
            except Exception as e:
                print_colored(text=f"❌ Problem refreshing TABLE '{table}'\n{e}", color="RED")
        print()
    
    except Exception as e:
        error_info(e)


def csv_import(files, tables, sequences):
    try:
        for file_path, table, sequence in zip(files, tables, sequences):
            try:
                execute_command(sql=queries.IMPORT_COMMAND.format(TABLE=table, FILE=file_path), capture=True)
                print_colored(text=f"✅ DATA from {file_path} imported INTO {table}", color="GREEN")
                if sequence:
                    update_sequence(show=False)
            except Exception as e:
                print_colored(text=f"❌ Problem with importing DATA TO {table} FROM {file_path}\n{e}", color="RED")
        print()
    
    except Exception as e:
        error_info(e)


def csv_export(choice):
    try:
        export_options = {
            'backup': {
                'tables': config['DB_tables'],
                'files': (config['MT_backup_location'], config['HT_backup_location']),
                'values' : (True, True),
                'export_completed' : True,
                'export_not_needed' : True,
                "reset" : lambda : None
            },
            #? all
            config['table_choice'][0]: {
                'tables': config['DB_tables'],
                'files': (config['MT_location'], config['HT_location']),
                'values' : (Tracker.status(what='M'), Tracker.status('H')),
                'export_completed' : True,
                'export_not_needed' : True,
                "reset" : lambda : Tracker.reset()
            },
            #? main
            config['table_choice'][1]: {
                'tables': (config['DB_tables'][0],),
                'files': (config['MT_location'],),
                'values' : (Tracker.status(what='M'),),
                'export_completed' : True,
                'export_not_needed' : True,
                "reset" : lambda : Tracker.reset(what='M')
            },
            #? history
            config['table_choice'][2]: {
                'tables': (config['DB_tables'][1],),
                'files': (config['HT_location'],),
                'values' : (Tracker.status('H'),),
                'export_completed' : True,
                'export_not_needed' : True,
                "reset" : lambda : Tracker.reset(what='H')
            }
        }

        if choice not in export_options.keys():
            print_colored(text=f"❌ No export option '{choice}'\n", color="RED")
            return
        
        for table, file_path, value in zip(export_options[choice]["tables"], export_options[choice]["files"], export_options[choice]["values"]):
            try:
                if not value:
                    if export_options[choice]["export_not_needed"]:
                        print_colored(text=f"✅ Data FROM '{table}' not exported - already up to date", color="YELLOW")
                    continue
                
                execute_command(sql=queries.EXPORT_COMMAND.format(TABLE=table, FILE=file_path), capture=True)
                if export_options[choice]["export_completed"]:
                    print_colored(text=f"✅ Data FROM '{table}' exported TO '{file_path}'", color="GREEN")
            except Exception as e:
                print_colored(text=f"❌ Problem with exporting data FROM '{table}' TO '{file_path}'\n{e}", color="RED")
        
        export_options[choice]["reset"]()       
        print()

    except Exception as e:
        error_info(e)


def psql():
    try:
        print_colored(text="💻 Opening PSQL shell ...", color="GREEN")
        execute_command(sql=None)
        print_colored(text="🛑 Exited psql\n", color="YELLOW")
    
    except Exception as e:
        error_info(e)


def update_sequence(show):
    try:
        result = execute_command(sql=queries.SEQUENCE_UPDATE, header=False, capture=True, text=True)
        if show:
            print_colored(text="ID sequence up to date", color="GREEN")
            print_colored(text=f"Next ID: {result.stdout.strip()}\n", color="CYAN")
    
    except Exception as e:
        error_info(e)


def uplaod_all(cmd):
    try:
        print_colored(text="Processing...", color="GREEN")
        subprocess.run(args=cmd, shell=True, check=True, capture_output=True)
        print_colored(text="Changes successfully uploaded to your GitHub repository\n", color="GREEN")

    except Exception as e:
        error_info(e)


def show_files(choice, limit):
    try:
        files_options = {
            'M' : config["MT_location"],
            'H' : config["HT_location"],
            'MB' : config["MT_backup_location"],
            'HB' : config["HT_backup_location"]
        }

        if choice.upper() not in files_options.keys():
            print_colored(text=f"❌ No choice '{choice}' available\n", color="RED")
            return

        command = ["powershell.exe",
                   "-Command", f"Import-Csv \"{files_options[choice]}\" -Header 'ID', 'RALLY', 'STAGE', 'CAR', 'TIME', 'CREATED'",
                   " | Format-Table -AutoSize"]
        if limit is not None and isinstance(limit, int):
            command.insert(-1, f" | Select-Object -Last {limit}")
        
        subprocess.run(args=command, shell=True, check=True)

    except Exception as e:
        error_info(e)


def end():
    try:
        csv_export(choice=config["table_choice"][0])

        print_colored(text="Have a great rest of your day Sir", color="CYAN")
        sys.exit()
    
    except Exception as e:
        error_info(e)
        