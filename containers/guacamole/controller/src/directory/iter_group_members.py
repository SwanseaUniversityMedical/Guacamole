import logging
import typing
import ldap
from ldap.ldapobject import SimpleLDAPObject
from ldap_filter import Filter

from .iter_search import ldap_iter_search


def ldap_iter_group_members(
    client: SimpleLDAPObject,
    group_base: str,
    group_filter: str,
    group_search_filter: str,
    user_base: str,
    user_filter: str,
    member_attribute: str,
    attrlist: typing.List[str],
    page_size: int,
    visited_dns: typing.Set[str] = None
):

    # Initialize a dn cache if one doesn't exist
    if visited_dns is None:
        visited_dns = set()

    # Filter an iterator so repeated dn's are skipped
    def visit(value) -> bool:
        dn, attr = value
        if dn in visited_dns:
            logging.debug(f"skipping {dn=}")
            return False
        visited_dns.add(dn)
        return True

    # Validate the filter for what is a valid user (further limited to under the user base)
    user_filter = Filter.parse(user_filter)

    # Validate the filter for what is a valid group (further limited to under the group base)
    group_filter = Filter.parse(group_filter)

    # Validate the top level group search filter (for this level of the recursion) with the
    # global group_filter for what is a valid group
    group_search_filter = Filter.AND([group_filter, Filter.parse(group_search_filter)])

    # Iterate over the top level groups that return in the group base from
    # the group filter
    for group_dn, group in filter(visit, ldap_iter_search(
        client=client,
        base=group_base,
        scope=ldap.SCOPE_SUBTREE,
        filterstr=group_search_filter.to_string(),
        attrlist=[member_attribute],
        page_size=page_size
    )):

        # Loop over the immediate members of the group under the group base
        for member_dn in group.get(member_attribute, list()):

            # Build a filter for testing the search object's dn is equal to the current member's dn
            member_dn_filter = Filter.attribute("distinguishedName").equal_to(member_dn)

            # If the member DN is a group then yielding from the recursion will
            # iterate over the nested members

            yield from filter(visit, ldap_iter_group_members(
                client=client,
                group_base=group_base,
                group_filter=group_filter.to_string(),
                group_search_filter=member_dn_filter.to_string(),
                user_base=user_base,
                user_filter=user_filter.to_string(),
                member_attribute=member_attribute,
                attrlist=attrlist,
                page_size=page_size,
                visited_dns=visited_dns
            ))

            # If the member DN is a person then yielding from the search under the
            # user base will iterate once for the member

            user_dn_filter = Filter.AND([user_filter, member_dn_filter])

            yield from filter(visit, ldap_iter_search(
                client=client,
                base=user_base,
                scope=ldap.SCOPE_SUBTREE,
                filterstr=user_dn_filter.to_string(),
                attrlist=attrlist,
                page_size=page_size
            ))
