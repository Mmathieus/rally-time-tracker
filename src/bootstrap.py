from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
src_path = ROOT / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import config as cnfg

import utils.menu as mm

import database.tools.status as stts


cnfg.db_state = stts.get_current_db_state()

if cnfg.config['dashboard_on_startup']:
    mm.print_dashboard(with_new_status_dict=False)



# import database.others.executor as exe
# from config import config


# db_status = {
#     'database': { 
#         'exists': False,
#         'size': None
#     },
#     'timings': {
#         'exists': False,
#         'size': None,
#         'records': None,
#         'data_size': None
#     },
#     'timings_history': {
#         'exists': False,
#         'size': None,
#         'records': None,
#         'data_size': None
#     }
# }

# DB_NAME = config['db_connection']['database']
# TABLES = ("timings", "timings_history")


# result = exe.execute_query(sql=f"SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}');", header=False, capture=True)
# if result.stdout.strip() == 't':
#     db_status['database']['exists'] = True

# if db_status['database']['exists']:
#     for table_name in TABLES:
#         result = exe.execute_query(sql=f"SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}');", header=False, capture=True)
#         if result.stdout.strip() == 't':
#             db_status[table_name]['exists'] = True


# if db_status['database']['exists']:
#     result = exe.execute_query(sql=f"SELECT pg_database_size('{DB_NAME}');", header=False, capture=True)
#     db_status['database']['size'] = int(result.stdout.strip())

# for table_name in TABLES:
#     if db_status[table_name]['exists']:
#         TABLE_STATS_QUERY = f"""
#             SELECT 
#                 pg_total_relation_size('{table_name}'),
#                 pg_relation_size('{table_name}'),
#                 (SELECT COUNT(*) FROM {table_name});
#         """
#         result = exe.execute_query(sql=TABLE_STATS_QUERY, header=False, capture=True)
#         stats = result.stdout.strip().split('|')
        
#         db_status[table_name]['size'] = int(stats[0].strip())
#         db_status[table_name]['data_size'] = int(stats[1].strip())
#         db_status[table_name]['records'] = int(stats[2].strip())

# config['db_status'] = db_status

# # print(config)