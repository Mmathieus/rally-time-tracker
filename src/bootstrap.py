import src.utils.formatter as ff

ff.print_colored(text="LOADING...\n", color="GREEN")

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
src_path = ROOT / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


import config as cnfg
import database.tools.state as stt
import services.dashboard as dshbrd

stt.capture_current_db_state()

if cnfg.config['dashboard_on_startup']:
    dshbrd.display_dashboard(refresh_db_state=False)
