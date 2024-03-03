import logging
import typing

from ldap.controls import SimplePagedResultsControl
from ldap.ldapobject import SimpleLDAPObject
from ldap_filter import Filter


def ldap_iter_search(
    client: SimpleLDAPObject,
    base: str,
    scope,
    filterstr: str,
    attrlist: typing.List[str],
    page_size: int
):
    # Escape the base for the search
    base = Filter.escape(base)

    # Validate the filter for the search
    filterstr = Filter.parse(filterstr)

    # Escape the list of return attrs
    attrlist = [Filter.escape(a) for a in attrlist]

    # Set up paging hooks for iterating over long results
    req_ctrl = SimplePagedResultsControl(
        True,
        size=page_size,
        cookie=""
    )

    known_ldap_resp_ctrls = {
        SimplePagedResultsControl.controlType :SimplePagedResultsControl,
    }

    # Make the initial query of the first page of results
    msgid = client.search_ext(
        base=base,
        scope=scope,
        filterstr=filterstr.to_string(),
        attrlist=attrlist,
        serverctrls=[req_ctrl]
    )

    # Consume pages of results until exhausted
    page = 0
    while True:
        page += 1

        # Retrieve the next page of results
        rtype, rdata, rmsgid, serverctrls = client.result3(
            msgid, resp_ctrl_classes=known_ldap_resp_ctrls
        )

        # Decode the page of results from bytes to strings yielding each record
        for dn, attrs in rdata:
            yield dn, { key: list(map(lambda x: x.decode(), value)) for key, value in attrs.items() }

        # Prepare to request the next page of results
        pctrls = [c for c in serverctrls if c.controlType == SimplePagedResultsControl.controlType]
        if pctrls:

            if pctrls[0].cookie:

                # Request the next page of results
                req_ctrl.cookie = pctrls[0].cookie
                msgid = client.search_ext(
                    base=base,
                    scope=scope,
                    filterstr=filterstr.to_string(),
                    attrlist=attrlist,
                    serverctrls=[req_ctrl]
                )

            else:
                # There are no more pages of results
                break

        else:
            logging.warning("server ignores RFC 2696 control")
            break
