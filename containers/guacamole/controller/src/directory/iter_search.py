import typing

from ldap3 import Connection
from ldap_filter import Filter


def ldap_iter_search(
    client: Connection,
    base: str,
    scope,
    search_filter: str,
    attributes: typing.List[str],
    paged_size: int
):
    # Escape the base for the search
    base = Filter.escape(base)

    # Validate the filter for the search
    search_filter = Filter.parse(search_filter)

    # Escape the list of return attrs
    attributes = [Filter.escape(a) for a in attributes]

    yield from client.extend.standard.paged_search(
        search_base=base,
        search_filter=search_filter.to_string(),
        search_scope=scope,
        attributes=attributes,
        paged_size=paged_size
    )
