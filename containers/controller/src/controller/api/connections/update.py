
import json
import logging
from urllib.parse import quote

import requests

from ..build_url import build_url
from ..error import APIConnectionDoesNotExistError


def api_update_connection(
    hostname: str,
    port: int,
    token: str,
    data_source: str,
    conn_id: int,
    conn_name: str,
    conn_protocol: str,
    conn_parent: str,
    conn_hostname: str,
    conn_port: int
):

    logging.debug(f"Updating connection {conn_name=} {conn_id=}")
    response = requests.put(
        build_url(
            scheme="http",
            netloc=f"{hostname}:{port}",
            path=f"/api/session/data/{quote(data_source)}/connections/{quote(str(conn_id))}",
            query=dict(
                token=token
            )
        ),
        data=json.dumps(dict(
            identifier=str(conn_id),
            name=conn_name,
            parentIdentifier=conn_parent,
            protocol=conn_protocol,
            parameters={
                "hostname": conn_hostname,
                "port": str(conn_port)
            },
            attributes={

            }
        )),
        verify=False,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code in (500,):
        ex = RuntimeError(("Bad status code!", response.status_code, response.text))
        logging.exception("Bad status code!", exc_info=ex)
        raise ex

    if response.status_code not in (204,):
        # TODO this exception catches too much
        ex = APIConnectionDoesNotExistError(("Bad status code!", response.status_code, response.text))
        logging.exception("Bad status code!", exc_info=ex)
        raise ex
