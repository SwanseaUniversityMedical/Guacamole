import logging
from urllib.parse import quote

import requests

from ..build_url import build_url
from ..error import APIUserDoesNotExistError


def api_delete_user(
    hostname: str,
    port: int,
    token: str,
    data_source: str,
    username: str
):

    logging.debug(f"Delete user {username=}")
    response = requests.delete(
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

    if response.status_code not in (204,):
        # TODO this exception catches too much
        ex = APIUserDoesNotExistError(("Bad status code!", response.status_code, response.text))
        logging.exception("Bad status code!", exc_info=ex)
        raise ex
