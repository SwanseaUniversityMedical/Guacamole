
import json
import logging
from urllib.parse import quote

import requests

from ..build_url import build_url
from ..error import APIConnectionDoesNotExistError


def api_get_connection(
    hostname: str,
    port: int,
    token: str,
    data_source: str,
    conn_id: int
) -> dict:

    logging.debug(f"Get connection {conn_id=}")
    response = requests.get(
        build_url(
            scheme="http",
            netloc=f"{hostname}:{port}",

            path=f"/api/session/data/{quote(data_source)}/connections/{quote(str(conn_id))}",
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
        ex = APIConnectionDoesNotExistError(("Bad status code!", response.status_code, response.text))
        logging.exception("Bad status code!", exc_info=ex)
        raise ex

    response = json.loads(response.text)
    logging.debug(f"{response=}")
    return response

def api_get_connection_parameters(
    hostname: str,
    port: int,
    token: str,
    data_source: str,
    conn_id: int
) -> dict:

    logging.debug(f"Get connection parameters {conn_id=}")
    response = requests.get(
        build_url(
            scheme="http",
            netloc=f"{hostname}:{port}",
            path=f"/api/session/data/{quote(data_source)}/connections/{quote(str(conn_id))}/parameters",
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
        ex = APIConnectionDoesNotExistError(("Bad status code!", response.status_code, response.text))
        logging.exception("Bad status code!", exc_info=ex)
        raise ex

    response = json.loads(response.text)
    logging.debug(f"{response=}")
    return response
