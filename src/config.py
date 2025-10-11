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


DB_NAME = config['database']['credentials']['database']
DB_ALIAS = config['database']['reference']

def update_db_name_globally() -> None:
    global DB_NAME
    DB_NAME = config['database']['credentials']['database']


PRIMARY_TB_NAME = "timings"
PRIMARY_TB_ALIAS = config['table']['reference']['primary_table']

HISTORY_TB_NAME = "timings_history"
HISTORY_TB_ALIAS = config['table']['reference']['history_table']

TABLE_MAPPING = {
    PRIMARY_TB_ALIAS: PRIMARY_TB_NAME,
    HISTORY_TB_ALIAS: HISTORY_TB_NAME
}

def get_tb_name(table) -> str:
    return TABLE_MAPPING[table]

BOTH_TABLES = (PRIMARY_TB_ALIAS, HISTORY_TB_ALIAS)

TABLES_ALIAS = config['table']['reference']['both_tables']

EVERYTHING_ALIAS = config['other_reference']['everything']


COMMANDS_ALIAS = config['other_reference']['commands']


WRC_RALLIES = config['rally-data']['rallies']

def get_rallies():
    return list(WRC_RALLIES.keys())

def get_stages(rally=None) -> list[str]:
    # All STAGES -> no RALLY typed
    if not rally:
        stage_options = []
        for stages in WRC_RALLIES.values():
            stage_options.extend(stages)
        return stage_options

    # STAGES for specific RALLY
    if rally in WRC_RALLIES:
        return WRC_RALLIES[rally]
    
    # RALLY typed but not recognized -> no corresponding STAGES
    return []


WRC_CARS = config['rally-data']['cars']
