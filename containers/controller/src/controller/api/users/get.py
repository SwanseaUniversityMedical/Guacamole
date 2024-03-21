
import json
import logging
from urllib.parse import quote

import requests

from ..build_url import build_url
from ..error import APIUserDoesNotExistError


def api_get_user(
    hostname: str,
    port: int,
    token: str,
    data_source: str,
    username: str,
) -> dict:

    logging.debug(f"Get user {username=}")
    response = requests.get(
        build_url(
            scheme="http",
            netloc=f"{hostname}:{port}",

            path=f"/api/session/data/{quote(data_source)}/users/{quote(username)}",
            query=dict(
                token=token
            )
        ),
        verify=False,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code not in (200,):
        # TODO this exception catches too much
        ex = APIUserDoesNotExistError(("Bad status code!", response.status_code, response.text))
        logging.exception("Bad status code!", exc_info=ex)
        raise ex

    response = json.loads(response.text)
    logging.debug(f"{response=}")
    return response


def api_get_user_effective_permissions(
    hostname: str,
    port: int,
    token: str,
    data_source: str,
    username: str,
) -> dict:

    logging.debug(f"Get user effective permissions {username=}")
    response = requests.get(
        build_url(
            scheme="http",
            netloc=f"{hostname}:{port}",

            path=f"/api/session/data/{quote(data_source)}/users/{quote(username)}/effectivePermissions",
            query=dict(
                token=token
            )
        ),
        verify=False,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code not in (200,):
        # TODO this exception catches too much
        ex = APIUserDoesNotExistError(("Bad status code!", response.status_code, response.text))
        logging.exception("Bad status code!", exc_info=ex)
        raise ex

    response = json.loads(response.text)
    logging.debug(f"{response=}")
    return response
