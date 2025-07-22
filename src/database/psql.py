import database.others.executor as exe
import utils.formatter as ff

def psql_exec():
    ff.print_colored(text="OPENING PSQL SHELL...\n", color="GREEN")
    exe.execute_query(sql=None)
    ff.print_colored(text="EXITED PSQL SHELL.\n", color="GREEN")