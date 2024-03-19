from .get_connections_by_manifest import get_connections_by_manifest
from .get_unique_users import get_unique_users
from .get_users_by_manifest import get_users_by_manifest
from .get_manifests import get_manifests
from .sync_users import sync_users

from ..api import API
from ..directory import LDAP


def sync(
    ldap: LDAP,
    api: API,
    kube_namespace: str
):

    manifests = get_manifests(
        namespace=kube_namespace)

    expected_users_by_manifest = get_users_by_manifest(
        ldap=ldap, manifests=manifests)

    expected_users = get_unique_users(
        users_by_manifest=expected_users_by_manifest)

    sync_users(
        api=api, ldap=ldap, expected_users=expected_users)

    expected_connections_by_manifest = get_connections_by_manifest(
        namespace=kube_namespace, manifests=manifests)

    if expected_connections_by_manifest:
        pass
