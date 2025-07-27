import src.bootstrap

import utils.inputter as ii
import utils.formatter as ff
import utils.menu as mm

import database.select as slct
import database.create_refresh_drop as crd
import database.import_ as imprt 
import database.export as exprt
import database.history as hstr
import database.tools.psql as psql

import services.restart as rstrt
import services.end as end
import services.dashboard as dshbrd

import traceback

# actions = {
#     '.' : {
#         "emoji" : '🔍',
#         "calls" : {
#             '0' : lambda : manager.GET_manager(searching_term=None),
#             '1' : lambda ST : manager.GET_manager(searching_term=ST),
#             '2' : lambda R, S : execs.get(rally=upper_casing(R), stage=upper_casing(S))
#         },
#         "info" : ("", "[rally/stage]", "[rally] [stage]")
#     },
#     'add' : {
#         "emoji" : '🆕',
#         "calls" : {
#             '0' : lambda : manager.INSERT_manager(data_obtained=False, record=[]),
#             '4' : lambda R, S, C, T : manager.INSERT_manager(data_obtained=True, record=[R,S,C,T])
#         },
#         "info" : ("", "[rally] [stage] [car] [time]")
#     },
#     'history' : {
#         "emoji" : '📜',
#         "calls" : {
#             '0' : lambda : manager.HISTORY_manager(),
#             '1' : lambda S : execs.history(stage=upper_casing(S))
#         },
#         "info" : ("", "[stage]")
#     },
#     'access' : {
#         "emoji" : '🗑️',
#         "calls" : {
#             '1' : lambda TC : manager.ACCESS_manager(table_choice=TC),
#             '2' : lambda T, I : execs.access(table=T, ids=[int(I)], look=False)
#         },
#         "info" : (f"[{MAIN}/{HISTORY}]", f"[{MAIN}/{HISTORY}] [id]")
#     },
#     'help' : {
#         "emoji" : '❓',
#         "calls" : {
#             '0' : lambda : help(specific_command=None),
#             '1' : lambda C : help(specific_command=C)
#         },
#         "info" : ("", "[command]")
#     },
#     'rst' : {
#         "emoji" : '🔄',
#         "calls" : {
#              '0' : lambda : execs.program_reset()
#         },
#         "info" : ("",)
#     },
#     'clear' : {
#         "emoji" : '🧹',
#         "calls" : {
#             '1' : lambda TC : manager.CLEAR_manager(table_choice=TC)
#         },
#         "info" : (f"[{ALL}/{MAIN}/{HISTORY}]",)
#     },
#     'import' : {
#         "emoji" : '📥',
#         "calls" : {
#             '1' : lambda T : manager.IMPORT_manager(table_choice=T, file_path=None),
#             '2' : lambda FP, T : manager.IMPORT_manager(table_choice=T, file_path=FP)
#         },
#         "info" : (f"[{ALL}/{MAIN}/{HISTORY}]",
#                   f"[filepath] [{ALL}/{MAIN}/{HISTORY}]")
#     },
#     'psql' : {
#        "emoji" : '🐘',
#        "calls" : {
#             '0' : lambda : execs.psql()
#         },
#         "info" : ("",)
#     },
#     'save' : {
#         "emoji" : '💾',
#         "calls" : {
#             '0' : lambda : (execs.csv_export(choice="all"), execs.csv_export(choice="backup")),
#             '1' : lambda C : execs.csv_export(choice=C)
#         },
#         "info" : ("", f"[backup/{ALL}/{MAIN}/{HISTORY}]")
#     },
#     'sequence' : {
#         "emoji" : '🆔',
#         "calls" : {
#             '0' : lambda : execs.update_sequence(show=True)
#         },
#         "info" : ("",)
#     },
#     'upload' : {
#         "emoji" : '🐙',
#         "calls" : {
#             '0' : lambda : manager.UPLAOD_manager(choice=config["table_choice"][0], message=None),
#             '1' : lambda C : manager.UPLAOD_manager(choice=C, message=None),
#             '2' : lambda C, M : manager.UPLAOD_manager(choice=C, message=M)
#         },
#         "info" : ("", "[data/code]", "[data/code] [message]")
#     },
#     'show' : {
#         "emoji" : '👀',
#         "calls" : {
#             '1' : lambda C : execs.show_files(choice=C.upper(), limit=10),
#             '2' : lambda C, L : execs.show_files(choice=C.upper(), limit=L)
#         },
#         "info" : ("[M/H/MB/HB]", "[M/H/MB/HB] [limit]")
#     },
#     'end' : {
#         "emoji" : '🛑',
#         "calls" : {
#             '0' : lambda : execs.end()
#         },
#         "info" : ("",)
#     }
# }


commands = {
    'select' : {
        'emoji': '🔍',
        'calls': {
            0: lambda: slct.select_manager(),
            1: lambda ST: slct.select_manager(search_term=ST),
            2: lambda R, S: slct.select_exec(rally=ff.upper_casing(term=R), stage=ff.upper_casing(term=S))
        },
        'args': {
            0: (),
            1: ("[search_term]",),
            2: ("[rally]", "[stage]") 
        }
    },
    'history' : {
        'emoji': '📜',
        'calls': {
            0: lambda: hstr.history_manger(),
            1: lambda S: hstr.history_manger(stage=S)
        },
        'args': {
            0: (),
            1: ("[stage]",) 
        }
    },
    'create' : {
        'emoji': '✳️',
        'calls': {
            1: lambda T: crd.create_exec(target=T)
        },
        'args': {
            1: ("[table/db]",)
        }
    },
    'refresh': {
        'emoji': '🔄',
        'calls': {
            1: lambda T: crd.refresh_manager(table=T),
            2: lambda T, KD: crd.refresh_manager(table=T, keep_data=KD)
        },
        'args': {
            1: ("[table]",),
            2: ("[table]", "[data_decision]")
        }
    },
    'drop' : {
        'emoji': '💣',
        'calls': {
            1: lambda T : crd.drop_exec(target=T)
        },
        'args': {
            1: ("[table/db]",)
        }
    },
    'import': {
        'emoji': '📥',
        'calls': {
            1: lambda T: imprt.import_manager(table=T),
            2: lambda T, M: imprt.import_manager(table=T, method=M)
        },
        'args': {
            1: ("[table]",),
            2: ("[table]", "[method]")
        }
    },
    'export': {
        'emoji': '📄',
        'calls': {
            1: lambda T: exprt.export_manager(table=T),
            2: lambda T, M: exprt.export_manager(table=T, method=M)
        },
        'args': {
            1: ("[table]",),
            2: ("[table]", "[method]")
        }
    },
    'dash': {
        'emoji': '📊',
        'calls': {
            0: lambda: dshbrd.render_dashboard()
        },
        'args': {
            0: ()
        }
    },
    'restart': {
        'emoji': '🔄',
        'calls': {
            0: lambda: rstrt.restart_exec()
        },
        'args': {
            0: ()
        }
    },
    'psql': {
        'emoji': '🐘',
        'calls': {
            0: lambda: psql.psql_exec()
        },
        'args': {
            0: ()
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
            0: lambda: end.end_exec()
        },
        'args': {
            0: ()
        }
    }
}
commands['help']['calls'][0] = lambda: mm.display_main_menu(commands_dict=commands)
commands['help']['calls'][1] = lambda C: mm.display_command_arguments(command=C, commands_dict=commands)


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
        ff.print_colored(text=f"Detaily:\n{traceback.format_exc()}\n", color="YELLOW")
