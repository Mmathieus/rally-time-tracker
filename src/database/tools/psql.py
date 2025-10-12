import utils.formatter as ff

import database.tools.executor as exe
import database.tools.other as othr


def psql_exec() -> None:
    all_ok, info_message = othr.get_db_exists_state()
    if not all_ok:
        ff.print_colored(text=f"PSQL SHELL NOT AVAILABLE. {info_message}\n", color="YELLOW")
        return

    ff.print_colored(text="OPENING PSQL SHELL...\n", color="GREEN")
    exe.execute_query(sql=None)
    ff.print_colored(text="EXITED PSQL SHELL.\n", color="GREEN")