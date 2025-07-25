from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
config_path = ROOT / "config.json"
with config_path.open('r', encoding='utf-8') as file:
    config = json.load(file)

db_state = None