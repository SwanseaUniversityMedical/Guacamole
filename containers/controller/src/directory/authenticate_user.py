import logging
from ldap3 import ALL, Connection, Server


def ldap_authenticate_user(
    hostname: str,
    port: int,
    username: str,
    password: str
) -> Connection:

    logging.info("connecting to ldap server")
    server = Server(host=hostname, port=port, use_ssl=True, get_info=ALL)

    logging.info("binding user")
    client = Connection(server, user=username, password=password, auto_bind=True)
    client.start_tls()

    return client
