import logging

from .get_unique_users import get_unique_users
from ..database import Database


def sync_users(
    database: Database,
    expected_users_by_manifest: dict
):

    logging.info("Syncing users")

    expected_users = get_unique_users(users_by_manifest=expected_users_by_manifest)

    observed_users = database.list_users()

    # Add users via database
    for user in expected_users.values():

        database.create_or_update_user(
            username=user["username"],
            fullname=user["fullname"],
            email=user["email"],
            organization=f"MANAGED-BY: {database.username}",
            role="MANAGED USER"
        )

    # Cull users
    for observed_user in observed_users.values():
        if (observed_user["username"] not in expected_users) and (observed_user["username"] != database.username):
            database.delete_user(username=observed_user["username"])
