from pathlib import Path
import json

# Setting PATH to config file
ROOT = Path(__file__).resolve().parent.parent
config_path = ROOT / "config.json"

with config_path.open('r', encoding='utf-8') as file:
    config = json.load(file)


# For DB Dashboard
db_state = {
    'database': { 
        'exists': None,
        'size': None
    },
    'timings': {
        'exists': None,
        'size': None,
        'data_size': None,
        'records': None
    },
    'timings_history': {
        'exists': None,
        'size': None,
        'data_size': None,
        'records': None
    }
}


DB_NAME = config['db_connection']['database']

TIMINGS_REAL = "timings"
TIMINGS_ALIAS = config['table_references']['timings']

TIMINGS_HISTORY_REAL = "timings_history"
TIMINGS_HISTORY_ALIAS = config['table_references']['timings_history']

EVERYTHING_ALIAS = config['everything_reference']

def update_db_name_globally() -> None:
    global DB_NAME
    DB_NAME = config['db_connection']['database']