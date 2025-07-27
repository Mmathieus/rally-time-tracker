import utils.formatter as ff
import database.tools.executor as exe


def psql_exec() -> None:
    ff.print_colored(text="OPENING PSQL SHELL...\n", color="GREEN")
    exe.execute_query(sql=None)
    ff.print_colored(text="EXITED PSQL SHELL.\n", color="GREEN")