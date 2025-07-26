from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
src_path = ROOT / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import config as cnfg

import utils.menu as mm

import database.tools.status as stts


stts.get_current_db_state()

if cnfg.config['dashboard_on_startup']:
    mm.print_dashboard(with_new_db_state=False)
