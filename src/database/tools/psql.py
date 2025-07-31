import utils.formatter as ff
import utils.other as oo

import database.tools.executor as exe


def psql_exec() -> None:
    all_ok, info_message = oo.get_db_exists_state()
    if not all_ok:
        ff.print_colored(text=f"PSQL SHELL NOT AVAILABLE. {info_message}\n", color="YELLOW")
        return

    ff.print_colored(text="OPENING PSQL SHELL...\n", color="GREEN")
    exe.execute_query(sql=None)
    ff.print_colored(text="EXITED PSQL SHELL.\n", color="GREEN")