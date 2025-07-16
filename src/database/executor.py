import subprocess
from config import config

# NOTE: Execute PostgreSQL query with configurable output options.
def execute_query(sql=None, pager=False, header=True, capture=False, text=True):
    command = [
        "psql",
        "-U", config.get('db_connection', {}).get('user'),
        "-d", config.get('db_connection', {}).get('database')
    ]

    if not pager:
        command.extend(["-P", "pager=off"])

    if not header:
        command.append("-t")
    
    if sql is None:
        sql = "SELECT 'No SQL provided' AS message"
    command.extend(["-c", sql])

    return subprocess.run(args=command, check=True, capture_output=capture, text=text)

# PSQL FLAGS REFERENCE:
# -U username    : Connect as specified user
# -d database    : Connect to specified database
# -P pager=off   : Disable pager (show all output at once)
# -t             : tuples_only mode (no headers/footers)
# -c "command"   : Execute command and exit

# SUBPROCESS FLAGS REFERENCE:
# check=True          : Raise CalledProcessError if command fails
# capture_output=True : Capture stdout/stderr (don't show in terminal)
# text=True           : Return string output instead of bytes