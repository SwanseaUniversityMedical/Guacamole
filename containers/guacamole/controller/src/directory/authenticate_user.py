import logging
import ldap
from ldap.ldapobject import SimpleLDAPObject

from ..utils import build_url


def ldap_authenticate_user(
    hostname: str,
    port: str,
    username: str,
    password: str
) -> SimpleLDAPObject:

    logging.info("connecting to ldap server")
    client = ldap.initialize(
        build_url(
            scheme="ldap",
            netloc=f"{hostname}:{port}"
        )
    )

    logging.info("binding user")
    result = client.bind_s(
        who=username,
        cred=password
    )
    logging.debug(f"{result=}")

    return client

