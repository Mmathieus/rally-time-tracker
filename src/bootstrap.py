from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import database.others.executor as exe
from config import config


db_status = {
    'database': False,
    'timings': False,
    'timings_history': False
}

DATABASE_EXISTS_QUERY = f"""
    SELECT EXISTS(
        SELECT 1 FROM pg_database WHERE datname = '{config['db_connection']['database']}'
    ) AS database_exists;
"""

TABLE_EXISTS_QUERY = """
    SELECT EXISTS(
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = '{table_name}'
    ) AS table_exists;
"""

answer = exe.execute_query(sql=DATABASE_EXISTS_QUERY, header=False, capture=True)
if answer.stdout.strip() == 't':
    db_status['database'] = True

for table_name in ['timings', 'timings_history']:
    result = exe.execute_query(sql=TABLE_EXISTS_QUERY.format(table_name=table_name), header=False, capture=True)
    if result.stdout.strip() == 't':
        db_status[table_name] = True

config['db_status'] = db_status
