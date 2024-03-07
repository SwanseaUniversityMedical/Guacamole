
import json
import logging
from urllib.parse import quote

import requests

from ..build_url import build_url


def api_list_connections(
    hostname: str,
    port: int,
    token: str,
    data_source: str
) -> dict:

    logging.debug("List connections")
    response = requests.get(
        build_url(
            scheme="http",
            netloc=f"{hostname}:{port}",

            path=f"/api/session/data/{quote(data_source)}/connections",
            query=dict(
                token=token
            )
        ),
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
