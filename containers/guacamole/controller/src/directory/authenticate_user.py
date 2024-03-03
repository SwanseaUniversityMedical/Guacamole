import logging
import ldap
from ldap.ldapobject import SimpleLDAPObject


def ldap_authenticate_user(
    hostname: str,
    port: str,
    username: str,
    password: str
) -> SimpleLDAPObject:

    logging.info("authenticating user")
    client = ldap.initialize(f"ldap://{hostname}:{port}")
    result = client.bind_s(
        who=username,
        cred=password
    )
    logging.debug(f"{result=}")

    return client

