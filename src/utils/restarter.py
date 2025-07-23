import sys
import subprocess
import utils.formatter as ff

def restart_exec():
    ff.print_colored(text="RESTARTING PROGRAM...\n", color="GREEN")
    subprocess.run(args=["python", "-u", "main.py"], check=True)
    sys.exit(0)