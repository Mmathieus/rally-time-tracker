import src.bootstrap

import utils.formatter as ff
import utils.inputter as ii

import database.create_refresh_drop as crd
import database.insert as insrt
import database.select as slct
import database.history as hstr
import database.import_ as imprt 
import database.export as exprt
import database.delete as dlt
import database.tools.psql as psql
import database.tools.switch as swtch

import services.help as hlp
import services.dashboard as dshbrd
import services.restart as rstrt
import services.end as end

import traceback


def _parse_user_command(command_string) -> tuple[str, list[str], int]:
    parts = command_string.strip().split()
    
    if not parts:
        return "", [], 0
    
    command = parts[0]
    args = parts[1:] if len(parts) > 1 else []
    
    return command, args, len(args)


commands = {
    'create' : {
        'emoji': '🔨',
        'calls': {
            1: lambda T: crd.create_exec(target=T)
        },
        'args': {
            1: ("[table/db]",)
        }
    },
    'insert' : {
        'emoji': '✏️',
        'calls': {
            0: lambda: insrt.insert_manager(),
            4: lambda R, S, C, T: insrt.insert_manager(rally=R, stage=S, car=C, time=T)
        },
        'args': {
            0: (),
            4: ("[rally] [stage] [car] [time]",) 
        }
    },
    'select' : {
        'emoji': '🔍',
        'calls': {
            0: lambda: slct.select_manager(),
            1: lambda ST: slct.select_manager(search_term=ST),
            2: lambda ST, TO: slct.select_manager(search_term=ST, time_order=TO),
            3: lambda ST, TO, OL: slct.select_manager(search_term=ST, time_order=TO, order_limit=OL)
        },
        'args': {
            0: (),
            1: ("[search_term]",),
            2: ("[search_term]", "[time_order]"),
            3: ("[search_term]", "[time_order]", "[order_limit]")
        }
    },
    'history' : {
        'emoji': '📜',
        'calls': {
            0: lambda: hstr.history_manager(),
            1: lambda S: hstr.history_manager(stage=S)
        },
        'args': {
            0: (),
            1: ("[stage]",) 
        }
    },
    'import': {
        'emoji': '📥',
        'calls': {
            1: lambda T: imprt.import_manager(table=T),
            2: lambda T, M: imprt.import_manager(table=T, method=M),
            3: lambda T, M, O: imprt.import_manager(table=T, method=M, override=O)
        },
        'args': {
            1: ("[table]",),
            2: ("[table]", "[method]"),
            3: ("[table]", "[method]", "[override_data]")
        }
    },
    'export': {
        'emoji': '💾',
        'calls': {
            1: lambda T: exprt.export_manager(table=T),
            2: lambda T, M: exprt.export_manager(table=T, method=M)
        },
        'args': {
            1: ("[table]",),
            2: ("[table]", "[method]")
        }
    },
    'delete': {
        'emoji': '🗑️',
        'calls': {
            1: lambda T: dlt.delete_manager(table=T),
            2: lambda T, ID: dlt.delete_manager(table=T, record_id=ID)
        },
        'args': {
            1: ("[table]",),
            2: ("[table]", "[record_id]")
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
    'psql': {
        'emoji': '🐘',
        'calls': {
            0: lambda: psql.psql_exec()
        },
        'args': {
            0: ()
        }
    },
    'drop' : {
        'emoji': '❌',
        'calls': {
            1: lambda T : crd.drop_exec(target=T)
        },
        'args': {
            1: ("[table/db]",)
        }
    },
    'switch' : {
        'emoji': '⚡',
        'calls': {
            0: lambda: swtch.switch_manager(),
            1: lambda D : swtch.switch_manager(database=D)
        },
        'args': {
            0: (),
            1: ("[database_name]",)
        }
    },
    ### --- ###
    'help': {
        'emoji': '💡',
        'calls': {},
        'args': {
            0: (),
            1: ("[command]",)
        }
    },
    'dash': {
        'emoji': '🖥️',
        'calls': {
            0: lambda: dshbrd.display_dashboard()
        },
        'args': {
            0: ()
        }
    },
    'rst': {
        'emoji': '🔃',
        'calls': {
            0: lambda: rstrt.restart_program()
        },
        'args': {
            0: ()
        }
    },
    'end': {
        'emoji': '🛑',
        'calls': {
            0: lambda: end.end_program()
        },
        'args': {
            0: ()
        }
    }
}
commands['help']['calls'][0] = lambda: hlp.display_commands_menu(commands_dict=commands)
commands['help']['calls'][1] = lambda C: hlp.display_command_arguments_menu(command=C, commands_dict=commands)


ff.print_colored(text="Welcome back Sir\n", color="CYAN")

while True:
    try:
        request = ii.get_user_input(symbol='💬', prompt="", with_colon=False)
        command, args, args_count = _parse_user_command(command_string=request)
        
        if command in commands:
            if args_count in commands[command]['calls']:
                func = commands[command]['calls'][args_count]
                func(*args)
    
    except Exception as e:
        ff.print_colored(text=f"PROBLEM: {e}", color="YELLOW")
        ff.print_colored(text=f"Details:\n{traceback.format_exc()}\n", color="RED")
