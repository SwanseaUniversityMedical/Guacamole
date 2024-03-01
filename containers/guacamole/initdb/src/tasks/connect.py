import logging

import sqlalchemy
from sqlalchemy.engine import Engine, URL


def get_database_connection(
    postgres_hostname: str,
    postgres_port: str,
    postgres_database: str,
    postgres_user: str,
    postgres_password: str,
    **kwargs
) -> Engine:

    url = URL(
        drivername='postgresql',
        username=postgres_user,
        password=postgres_password,
        host=postgres_hostname,
        port=postgres_port,
        database=postgres_database,
        query={}
    )
    logging.debug(f"{url=}")
    return sqlalchemy.create_engine(url)
