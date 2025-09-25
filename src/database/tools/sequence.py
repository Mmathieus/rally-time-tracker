import config as cnfg
import database.tools.executor as exe


SEQUENCE_QUERY = "SELECT setval(pg_get_serial_sequence('timings', 'id'), {value})"


def update_sequence() -> None:
    timings_id, timings_history_id = _tables_current_max_ids()

    new_sequence_value = _determine_sequence_value(timings_value=timings_id, timings_history_value=timings_history_id)

    if new_sequence_value:
        exe.execute_query(sql=SEQUENCE_QUERY.format(value=new_sequence_value), header=False, capture=True)


def _tables_current_max_ids() -> tuple[int, int | None]:
    timings_id, timings_history_id = 0, None

    # Primary
    result = exe.execute_query(sql="SELECT MAX(id) FROM timings;", header=False, capture=True)
    potential_id = result.stdout.strip()

    if potential_id:
        timings_id = potential_id

    # History
    if cnfg.db_state['timings_history']['exists']:
        timings_history_id = 0
        
        result = exe.execute_query(sql="SELECT MAX(id) FROM timings_history;", header=False, capture=True)
        potential_id = result.stdout.strip()

        if potential_id:
            timings_history_id = int(potential_id)
    
    return int(timings_id), timings_history_id

def _determine_sequence_value(timings_value, timings_history_value) -> int | None:
    # Timings has NO RECORDS - Timings_history DOESN'T EXIST or has NO RECORD(S)
    if not timings_value and not timings_history_value:
        return None

    # Timings has NO RECORDS - Timings_history has RECORD(S)
    if not timings_value and timings_history_value:
        return timings_history_value
    
    ###########################

    # Timings has RECORD(S) - Timings_history DOESN'T EXIST or has NO RECORD(S)
    if timings_value and not timings_history_value:
        return timings_value
    
    # Timings has RECORD(S) - Timings_history has RECORD(S)
    return max(timings_value, timings_history_value)
