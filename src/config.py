from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
config_path = ROOT / "config.json"
with config_path.open('r', encoding='utf-8') as file:
    config = json.load(file)

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