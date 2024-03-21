
import json
import logging
from urllib.parse import quote

import requests

from ..build_url import build_url
from ..error import APIUserDoesNotExistError


def api_update_user(
    hostname: str,
    port: int,
    token: str,
    data_source: str,
    username: str,
    fullname: str,
    email: str,
    organization: str,
    role: str
):

    logging.debug(f"Updating user {username=}")
    response = requests.put(
        build_url(
            scheme="http",
            netloc=f"{hostname}:{port}",

            path=f"/api/session/data/{quote(data_source)}/users/{quote(username)}",
            query=dict(
                token=token
            )
        ),
        data=json.dumps(dict(
            username=username,
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

    if response.status_code not in (204,):
        # TODO this exception catches too much
        ex = APIUserDoesNotExistError(("Bad status code!", response.status_code, response.text))
        logging.exception("Bad status code!", exc_info=ex)
        raise ex
