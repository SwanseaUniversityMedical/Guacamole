import logging
import typing

from ldap.controls import SimplePagedResultsControl
from ldap.ldapobject import SimpleLDAPObject


def ldap_iter_search(
    client: SimpleLDAPObject,
    base: str,
    scope,
    filterstr: str,
    attrlist: typing.List[str],
    page_size: int
):
    req_ctrl = SimplePagedResultsControl(
        True,
        size=page_size,
        cookie=""
    )

    known_ldap_resp_ctrls = {
        SimplePagedResultsControl.controlType :SimplePagedResultsControl,
    }

    msgid = client.search_ext(
        base=base,
        scope=scope,
        filterstr=filterstr,
        attrlist=attrlist,
        serverctrls=[req_ctrl]
    )

    page = 0
    while True:
        page += 1

        logging.debug(f"fetching {page=}")
        rtype, rdata, rmsgid, serverctrls = client.result3(
            msgid, resp_ctrl_classes=known_ldap_resp_ctrls
        )

        yield from rdata

        pctrls = [c for c in serverctrls if c.controlType == SimplePagedResultsControl.controlType]
        if pctrls:

            if pctrls[0].cookie:
                logging.debug(f"requesting next page")
                req_ctrl.cookie = pctrls[0].cookie
                msgid = client.search_ext(
                    base=base,
                    scope=scope,
                    filterstr=filterstr,
                    attrlist=attrlist,
                    serverctrls=[req_ctrl]
                )

            else:
                logging.debug(f"no more pages")
                break

        else:
            logging.warning("server ignores RFC 2696 control")
            break
