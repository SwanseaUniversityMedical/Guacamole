import typing

from ldap3 import Connection

from .iter_group_members import ldap_iter_group_members
from .authenticate_user import ldap_authenticate_user


class LDAP:

    hostname: str
    port: int
    user_base_dn: str
    user_search_filter: str
    username_attribute: str
    fullname_attribute: str
    email_attribute: str
    group_base_dn: str
    group_search_filter: str
    member_attribute: str
    search_bind_dn: str
    search_bind_password: str
    paged_size: int
    client: Connection

    def __init__(self,
        hostname: str,
        port: int,
        user_base: str,
        user_filter: str,
        username_attribute: str,
        fullname_attribute: str,
        email_attribute: str,
        group_base: str,
        group_filter: str,
        member_attribute: str,
        username: str,
        password: str,
        paged_size: int
    ):

        self.hostname = hostname
        self.port = port
        self.user_base = user_base
        self.user_filter = user_filter
        self.username_attribute = username_attribute
        self.fullname_attribute = fullname_attribute
        self.email_attribute = email_attribute
        self.group_base = group_base
        self.group_filter = group_filter
        self.member_attribute = member_attribute
        self.username = username
        self.password = password
        self.paged_size = paged_size

        self.client = ldap_authenticate_user(
            hostname=self.hostname,
            port=self.port,
            username=self.username,
            password=self.password
        )

    def iter_group_members(self,
        group_search_filter: str,
        attributes: typing.List[str]
    ):
        yield from ldap_iter_group_members(
            client=self.client,
            group_base=self.group_base,
            group_filter=self.group_filter,
            group_search_filter=group_search_filter,
            user_base=self.user_base,
            user_filter=self.user_filter,
            member_attribute=self.member_attribute,
            attributes=attributes,
            paged_size=self.paged_size
        )
