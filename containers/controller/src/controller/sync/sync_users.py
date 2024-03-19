from ..api import API
from ..directory import LDAP


def sync_users(
    api: API,
    ldap: LDAP,
    expected_users: dict
):

    # Add users via api
    for user in expected_users.values():

        api.create_or_update_user(
            username=user["attributes"][ldap.username_attribute],
            fullname=user["attributes"][ldap.fullname_attribute],
            email=user["attributes"][ldap.email_attribute],
            organization="MANAGED",
            role="MANAGED"
        )
