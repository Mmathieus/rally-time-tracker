from config import config
from database.others import executor as exe
from utils import formatter as ff

DATABASE_NAME = config['db_connection']['database']

def create_database() -> None:
    query = f"CREATE DATABASE {DATABASE_NAME}"

    answer = exe.execute_query(sql=query, header=False, capture=True, check=False, postgres_db=True)

    if answer.stderr and "already exists" in answer.stderr.strip():
        ff.print_colored(text=f"DATABASE '{DATABASE_NAME}' NOT CREATED - ALREADY EXISTS.\n", color="YELLOW")
        return

    ff.print_colored(text=f"DATABASE '{DATABASE_NAME}' CREATED.\n", color="GREEN")

def drop_database() -> None:
    query = f"DROP DATABASE IF EXISTS {DATABASE_NAME}"

    answer = exe.execute_query(sql=query, header=False, capture=True, postgres_db=True)

    if answer.stderr and "does not exist" in answer.stderr.strip():
        ff.print_colored(text=f"DATABASE '{DATABASE_NAME}' NOT DROPPED - DOESN'T EXIST.\n", color="YELLOW")
        return

    ff.print_colored(text=f"DATABASE '{DATABASE_NAME}' DROPPED.\n", color="GREEN")