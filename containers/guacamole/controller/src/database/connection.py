import logging

import sqlalchemy
from sqlalchemy.engine import Engine, URL


def db_connection(
    hostname: str,
    port: int,
    database: str,
    username: str,
    password: str
) -> Engine:

    url = URL(
        drivername='postgresql',
        username=username,
        password=password,
        host=hostname,
        port=port,
        database=database,
        query=dict()
    )
    logging.debug(f"{url=}")
    return sqlalchemy.create_engine(url)
