import logging


def get_unique_users(
    users_by_manifest: dict
):
    # Flatten unique users by LDAP dn
    expected_users = {
        user["username"]: user
        for users in users_by_manifest.values()
        for user in users.values()
    }
    logging.info(f"Found {len(expected_users)} unique users across {len(users_by_manifest)} manifests")

    return expected_users
