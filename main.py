import src.bootstrap as bb

import database.select as ss
import database.create_refresh_drop as crd

import utils.formatter as ff
import utils.inputter as ii
import utils.menu as mm

# ss.SELECT_manager(searching_term=None)

import sys
# sys.exit(0)

import src.manager
import src.execs
from src.others import print_colored, error_info, upper_casing, Tracker
from src._config import config; ALL, MAIN, HISTORY = config["table_choice"]



# * Process input
def process_INPUT(user_input):
    segments = user_input.split()
    return segments[0], segments[1:], str(len(segments[1:]))  # command, arguments, arguments_count

# * Show HELP
def help(specific_command):
    if specific_command is None:
        separator = print_colored(text='|', color="CYAN", display=False)
        formatted_pairs = f" {separator} ".join(f"{value['emoji']} {command}" for command, value in actions.items())
        print(f"\n{separator} {formatted_pairs} {separator}\n")
        return
    
    if specific_command not in actions.keys():
        return print_colored(text=f"❌ Command '{specific_command}' not recognized\n", color="RED", display=False)

    def colored_HELP(command, args):
        command_color = "RED"
        arg_color = "YELLOW"

        output = ""
        print("\nCalling options:")
        for arg in args:
            output += f"-> {command} {arg}\n"

        for text, color in [('[', arg_color), (']', arg_color), (command, command_color)]:
            output = output.replace(text, print_colored(text=text, color=color, display=False))
        return output
    
    print(f"{colored_HELP(command=specific_command, args=actions[specific_command]['info'])}")


actions = {
    '.' : {
        "emoji" : '🔍',
        "calls" : {
            '0' : lambda : manager.GET_manager(searching_term=None),
            '1' : lambda ST : manager.GET_manager(searching_term=ST),
            '2' : lambda R, S : execs.get(rally=upper_casing(R), stage=upper_casing(S))
        },
        "info" : ("", "[rally/stage]", "[rally] [stage]")
    },
    'add' : {
        "emoji" : '🆕',
        "calls" : {
            '0' : lambda : manager.INSERT_manager(data_obtained=False, record=[]),
            '4' : lambda R, S, C, T : manager.INSERT_manager(data_obtained=True, record=[R,S,C,T])
        },
        "info" : ("", "[rally] [stage] [car] [time]")
    },
    'history' : {
        "emoji" : '📜',
        "calls" : {
            '0' : lambda : manager.HISTORY_manager(),
            '1' : lambda S : execs.history(stage=upper_casing(S))
        },
        "info" : ("", "[stage]")
    },
    'access' : {
        "emoji" : '🗑️',
        "calls" : {
            '1' : lambda TC : manager.ACCESS_manager(table_choice=TC),
            '2' : lambda T, I : execs.access(table=T, ids=[int(I)], look=False)
        },
        "info" : (f"[{MAIN}/{HISTORY}]", f"[{MAIN}/{HISTORY}] [id]")
    },
    'help' : {
        "emoji" : '❓',
        "calls" : {
            '0' : lambda : help(specific_command=None),
            '1' : lambda C : help(specific_command=C)
        },
        "info" : ("", "[command]")
    },
    'rst' : {
        "emoji" : '🔄',
        "calls" : {
             '0' : lambda : execs.program_reset()
        },
        "info" : ("",)
    },
    'clear' : {
        "emoji" : '🧹',
        "calls" : {
            '1' : lambda TC : manager.CLEAR_manager(table_choice=TC)
        },
        "info" : (f"[{ALL}/{MAIN}/{HISTORY}]",)
    },
    'import' : {
        "emoji" : '📥',
        "calls" : {
            '1' : lambda T : manager.IMPORT_manager(table_choice=T, file_path=None),
            '2' : lambda FP, T : manager.IMPORT_manager(table_choice=T, file_path=FP)
        },
        "info" : (f"[{ALL}/{MAIN}/{HISTORY}]",
                  f"[filepath] [{ALL}/{MAIN}/{HISTORY}]")
    },
    'psql' : {
       "emoji" : '🐘',
       "calls" : {
            '0' : lambda : execs.psql()
        },
        "info" : ("",)
    },
    'save' : {
        "emoji" : '💾',
        "calls" : {
            '0' : lambda : (execs.csv_export(choice="all"), execs.csv_export(choice="backup")),
            '1' : lambda C : execs.csv_export(choice=C)
        },
        "info" : ("", f"[backup/{ALL}/{MAIN}/{HISTORY}]")
    },
    'sequence' : {
        "emoji" : '🆔',
        "calls" : {
            '0' : lambda : execs.update_sequence(show=True)
        },
        "info" : ("",)
    },
    'upload' : {
        "emoji" : '🐙',
        "calls" : {
            '0' : lambda : manager.UPLAOD_manager(choice=config["table_choice"][0], message=None),
            '1' : lambda C : manager.UPLAOD_manager(choice=C, message=None),
            '2' : lambda C, M : manager.UPLAOD_manager(choice=C, message=M)
        },
        "info" : ("", "[data/code]", "[data/code] [message]")
    },
    'show' : {
        "emoji" : '👀',
        "calls" : {
            '1' : lambda C : execs.show_files(choice=C.upper(), limit=10),
            '2' : lambda C, L : execs.show_files(choice=C.upper(), limit=L)
        },
        "info" : ("[M/H/MB/HB]", "[M/H/MB/HB] [limit]")
    },
    'end' : {
        "emoji" : '🛑',
        "calls" : {
            '0' : lambda : execs.end()
        },
        "info" : ("",)
    }
}


commands = {
    'select' : {
        'emoji': '🔍',
        'calls': {
            0: lambda: ss._select_manager(),
            1: lambda ST: ss._select_manager(search_term=ST),
            2: lambda R, S: ss._select_exec(rally=ff.upper_casing(term=R), stage=ff.upper_casing(term=S))
        },
        'args': {
            0: (),
            1: ("[search_term]",),
            2: ("[rally]", "[stage]") 
        }
    },
    'create' : {
        'emoji': '✳️',
        'calls': {
            1: lambda W: crd._create_exec(what=W)
        },
        'args': {
            1: ("[main/history/db]",)
        }
    },
    'refresh': {
        'emoji': '🔄',
        'calls': {
            1: lambda T: crd._refresh_manager(table=T),
            2: lambda T, KD: crd._refresh_manager(table=T, keep_data=KD)
        },
        'args': {
            1: ("[main/history]",),
            2: ("[main/history]", "[keep/lose]")
        }
    },
    'drop' : {
        'emoji': '💣',
        'calls': {
            1: lambda W : crd._drop_exec(what=W)
        },
        'args': {
            1: ("[main/history/db]",)
        }
    },
    'help': {
        'emoji': '❓',
        'calls': {},
        'args': {
            0: (),
            1: ("[command]",)
        }
    },
    'end': {
        'emoji': '🛑',
        'calls': {
            0: lambda: sys.exit(0)
        },
        'args': {
            0: ()
        }
    }
}
commands['help']['calls'][0] = lambda: mm.display_main_menu(commands_dict=commands)
commands['help']['calls'][1] = lambda CN: mm.display_command_arguments(command_name=CN, commands_dict=commands)



ff.print_colored(text="Welcome back Sir\n", color="CYAN")

while True:
    try:
        request = ii.get_user_input(prompt="", symbol='💬', with_colon=False)
        command, args, args_count = ii.parse_command_input(input_string=request)
        
        if command in commands:
            if args_count in commands[command]['calls']:
                func = commands[command]['calls'][args_count]
                func(*args)
    
    except Exception as e:
        ff.print_colored(text=f"PROBLEM: {e}", color="RED")




while True:
    request = input("💬 ").strip()
    if not request:
        continue
    if request == 'q':
        break
    if request == 's':
        ss._select_manager(search_term=None)
    if request == "table":
        st._tables_manager(table_choice=None)
    if request == "table h":
        st._tables_manager(table_choice="history")
    if request == "table m":
        st._tables_manager(table_choice="main")
    if request == "table m drop":
        st.drop_TABLE(table="main")
    if request == "table h drop":
        st.drop_TABLE(table="history")
    if request == "table h refresh":
        st._tables_manager(table_choice="history", operation_choice="refresh")
    if request == "create database":
        db.create_database()
    if request == "drop database":
        db.drop_database()
    
    # command, args, arg_count = process_INPUT(user_input=request)
    # if command in actions:
    #     try:
    #         if arg_count in actions[command]["calls"]:
    #             actions[command]["calls"][arg_count](*args)
    #         #Tracker.look()
    #     except Exception as e:
    #         error_info(e)

