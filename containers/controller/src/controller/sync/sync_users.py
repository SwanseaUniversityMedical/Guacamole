import logging

from .get_unique_users import get_unique_users
from ..api import API
from ..directory import LDAP


def sync_users(
    api: API,
    expected_users_by_manifest: dict
):

    logging.info("Syncing users")

    expected_users = get_unique_users(users_by_manifest=expected_users_by_manifest)

    observed_users = api.list_users()

    # Add users via api
    for user in expected_users.values():

        api.create_or_update_user(
            username=user["username"],
            fullname=user["fullname"],
            email=user["email"],
            organization=f"MANAGED-BY: {api.username}",
            role="MANAGED USER"
        )

    # Cull users
    for observed_user in observed_users.values():
        if (observed_user["username"] not in expected_users) and (observed_user["username"] != api.username):
            api.delete_user(username=observed_user["username"])

