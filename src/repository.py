from pg import DB
from env import (
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PORT
    )


postgres_user: str | None = POSTGRES_USER
postgres_password: str | None = POSTGRES_PASSWORD
postgres_db: str | None = POSTGRES_DB
postgres_host: str | None = POSTGRES_HOST
postgres_port: str | None = POSTGRES_PORT

if postgres_user is None:
    raise EnvironmentError("'POSTGRES_USER' is not present")
if postgres_password is None:
    raise EnvironmentError("'POSTGRES_PASSWORD' is not present")
if postgres_db is None:
    raise EnvironmentError("'POSTGRES_DB' is not present")
if postgres_host is None:
    raise EnvironmentError("'POSTGRES_HOST' is not present")
if postgres_port is None:
    raise EnvironmentError("'POSTGRES_PORT' is not present")

db = DB(
    dbname=postgres_db,
    host=postgres_host,
    port=int(postgres_port),
    user=postgres_user,
    passwd=postgres_password,
)


def find_reply_by_language_and_project(language: str, project: str) -> str | None:
    query = db.query(
        f"""
        SELECT message, language FROM "Add_project_replies" 
        WHERE project_name='{project}'
        """
    )
    rows = query.dictresult()

    rows_by_language = list(filter(lambda x: x["language"] == language, rows))

    if len(rows_by_language) == 1:
        return rows_by_language[0]["message"]

    rows_by_language = list(filter(lambda x: x["language"] == "*", rows))

    if len(rows_by_language) == 1:
        return rows_by_language[0]["message"]

    return None
