import json
import logging
# import secrets
from urllib.parse import quote

import requests

from ..build_url import build_url


def api_create_user(
    hostname: str,
    port: int,
    token: str,
    data_source: str,
    username: str,
    fullname: str,
    email: str,
    organization: str,
    role: str
) -> dict:

    # PASSWORD MUST BE SET TO EMPTY STRING SO THAT AUTHENTICATION
    # IS HANDLED BY LDAP WITHOUT A BACKDOOR
    DISABLE_PASSWORD = ""

    # Could also set it to a long random password, the plaintext of which
    # is never stored anywhere since it is hashed and salted in the database
    # DISABLE_PASSWORD = secrets.token_hex(32)

    logging.debug(f"Creating user {username=}")
    response = requests.post(
        build_url(
            scheme="http",
            netloc=f"{hostname}:{port}",
            path=f"/api/session/data/{quote(data_source)}/users",
            query=dict(
                token=token
            )
        ),
        data=json.dumps(dict(
            username=username,
            password=DISABLE_PASSWORD,
            attributes={
                "guac-full-name": fullname,
                "guac-email-address": email,
                "guac-organization": organization,
                "guac-organizational-role": role
            }
        )),
        verify=False,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code not in (200,):
        ex = RuntimeError(("Bad status code!", response.status_code, response.text))
        logging.exception("Bad status code!", exc_info=ex)
        raise ex

    response = json.loads(response.text)
    logging.debug(f"{response=}")
    return response
