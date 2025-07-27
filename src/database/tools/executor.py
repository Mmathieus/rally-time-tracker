import config as cnfg
import subprocess


def execute_query(sql=None, pager=False, header=True, capture=False, text=True, check=True, postgres_db=False) -> subprocess.CompletedProcess:    
    command = [
        "psql",
        "-U", cnfg.config['db_connection']['user'],
        "-d", cnfg.config['db_connection']['database'] if not postgres_db else "postgres",
    ]

    if not pager:
        command.extend(["-P", "pager=off"])

    if not header:
        command.append("-t")
    
    if sql:
        command.extend(["-c", sql])

    return subprocess.run(args=command, check=check, capture_output=capture, text=text)

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
