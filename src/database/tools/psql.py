import utils.formatter as ff

import database.tools.executor as exe
import database.tools.state as stt


def psql_exec() -> None:
    # Check if DB exists
    if not stt.check_db_exists_state(
        info_message=ff.colorize(text="PSQL SHELL NOT AVAILABLE. {rest}\n", color="YELLOW")
    )[0]:
        return

    ff.print_colored(text="OPENING PSQL SHELL...\n", color="GREEN")
    exe.execute_query(sql=None)
    ff.print_colored(text="EXITED PSQL SHELL.\n", color="GREEN")