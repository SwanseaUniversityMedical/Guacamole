import json
import logging

import requests

from .build_url import build_url


def api_authenticate_user(
    hostname: str,
    port: int,
    username: str,
    password: str
) -> str:

    logging.info("authenticating user")
    response = requests.post(
        build_url(
            scheme="http",
            netloc=f"{hostname}:{port}",
            path="/api/tokens"
        ),
        data=dict(
            username=username,
            password=password
        ),
        verify=False,
        timeout=30,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    ).text

    response = json.loads(response)
    logging.debug(f"{response=}")

    token = response['authToken']
    logging.debug(f"{token=}")

    return token
