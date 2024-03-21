
from .get_users_by_manifest import get_users_by_manifest
from .get_manifests import get_manifests
from .sync_connections import sync_connections
from .sync_users import sync_users

from ..api import API
from ..directory import LDAP


def sync(
    ldap: LDAP,
    api: API,
    kube_namespace: str
):

    # Lookup GuacamoleConnection manifests from kubes
    manifests = get_manifests(namespace=kube_namespace)

    # Search LDAP for each GuacamoleConnection manifest to get its expected users
    expected_users_by_manifest = get_users_by_manifest(ldap=ldap, manifests=manifests)

    # For all the unique users create or update them using the Guacamole REST api
    # Set or update their `valid_until` field to expire if this sync starts failing
    sync_users(
        api=api,
        expected_users_by_manifest=expected_users_by_manifest
    )

    # For all the connections create or update them using the Guacamole REST api
    sync_connections(
        api=api,
        manifests=manifests,
        expected_users_by_manifest=expected_users_by_manifest
    )
