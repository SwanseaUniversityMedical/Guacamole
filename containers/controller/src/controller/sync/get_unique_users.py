import logging


def get_unique_users(
    users_by_manifest: dict
):
    # Flatten unique users by LDAP dn
    expected_users = {
        record["dn"]: record
        for records in users_by_manifest.values()
        for record in records
    }
    logging.info(f"Found {len(expected_users)} unique users across {len(users_by_manifest)} manifests")

    return expected_users
