import logging

from ..directory import LDAP


def get_users_by_manifest(
    ldap: LDAP,
    manifests: dict
):

    def record_fn(record):
        return dict(
            username=record["attributes"][ldap.username_attribute],
            fullname=record["attributes"][ldap.fullname_attribute],
            email=record["attributes"][ldap.email_attribute]
        )

    users_by_manifest = dict()
    for name, manifest in manifests.items():

        if not manifest["spec"]["ldap"]["enabled"]:
            logging.info(f"{name=} Skipping user membership lookup for manifest")
            continue

        group_search_filter = manifest["spec"]["ldap"]["groupFilter"]
        logging.info(f"Searching user membership for manifest {name} {group_search_filter=}")

        users_by_manifest[name] = {
            user["username"]: user for user in map(record_fn, ldap.iter_group_members(
                group_search_filter=group_search_filter,
                attributes=[
                    ldap.username_attribute,
                    ldap.fullname_attribute,
                    ldap.email_attribute
                ]
            ))
        }

        logging.info(f"Found {len(users_by_manifest[name])} users")

    return users_by_manifest
