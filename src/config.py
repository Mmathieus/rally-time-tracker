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


WRC_DICT = {
    "Monte-Carlo": ["Agnieres", "Luceram", "Col-De-Braus"],
    "Sweden": ["Torsby", "Vargasen", "Karlstad"],
    "Mexico": ["Media-Luna-R", "Ibarrilla", "Leon"],
    "Argentina": ["El-Condor", "Cuchilla-Nevada"],
    "Portugal": ["Fafe", "Viana-Do-Castelo", "Felgueiras", "Arganil", "Lousada"],
    "Italy": ["Baranta", "Lerno", "Ittiri"],
    "Kenya": ["Ngema", "Seyabei"],
    "Finland": ["Ouninpohja", "Horkka", "Arvaja", "Pihlajakoski", "Harju"],
    "New-Zealand": ["Te-Hutewai", "Batley", "Brooks", "Te-Akau-South"],
    "Turkey": ["Datca", "Cicekli", "Marmaris"],
    "Germany": ["Moselland", "Freisen", "Panzerplatte"],
    "Wales": ["Hafren", "Great-Orme" "Brenig"],
    "Japan": ["Okazaki", "Nagakute", "Shinshiro", "Shitara"]
}

def get_rallies():
    return list(WRC_DICT.keys())

def get_stages(rally=None) -> list[str]:
    # All STAGES -> no RALLY typed
    if not rally:
        stage_options = []
        for stages in WRC_DICT.values():
            stage_options.extend(stages)
        return stage_options

    # STAGES for specific RALLY
    if rally in WRC_DICT:
        return WRC_DICT[rally]
    
    # RALLY typed but not recognized -> no corresponding STAGES
    return []
