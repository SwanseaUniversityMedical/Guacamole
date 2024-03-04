import logging
from collections import namedtuple
from urllib.parse import urlencode, urlunparse


def build_url(
    scheme: str,
    netloc: str,
    path: str = "",
    params: str = "",
    query: dict = None,
    fragment: str = ""
):

    if query is None:
        query = dict()

    # namedtuple to match the internal signature of urlunparse
    Components = namedtuple(
        typename='Components',
        field_names=['scheme', 'netloc', 'path', 'params', 'query', 'fragment']
    )

    url = urlunparse(
        Components(
            scheme=scheme,
            netloc=netloc,
            path=path,
            params=params,
            query=urlencode(query),
            fragment=fragment
        )
    )

    logging.debug(f"{url=}")
    return url