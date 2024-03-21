
import json
import logging
from urllib.parse import quote

import requests

from ..build_url import build_url
from ..error import APIUserDoesNotExistError


def api_create_user_connection(
    hostname: str,
    port: int,
    token: str,
    data_source: str,
    username: str,
    conn_id: int
):

    logging.debug(f"Creating user connection {username=} {conn_id=}")
    response = requests.patch(
        build_url(
            scheme="http",
            netloc=f"{hostname}:{port}",
            path=f"/api/session/data/{quote(data_source)}/users/{quote(username)}/permissions",
            query=dict(
                token=token
            )
        ),
        data=json.dumps([
            dict(
                op="add",
                path=f"/connectionPermissions/{quote(conn_id)}",
                value="READ"
            )
        ]),
        verify=False,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code not in (204,):
        # TODO this exception catches too much
        ex = APIUserDoesNotExistError(("Bad status code!", response.status_code, response.text))
        logging.exception("Bad status code!", exc_info=ex)
        raise ex
