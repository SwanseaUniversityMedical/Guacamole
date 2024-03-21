import logging

from ..api import API


def sync_connections(
    api: API,
    manifests: dict,
    expected_users_by_manifest: dict
):
    logging.info("Syncing connections")

    observed_connections = api.list_connections()
    expected_connections = set()

    # Add connections via api
    for manifest_name, manifest in manifests.items():


        name = manifest["metadata"]["name"]
        namespace = manifest["metadata"]["namespace"]

        conn_protocol = manifest["spec"]["protocol"]
        conn_name = f"{namespace}/{name} - {conn_protocol}"

        logging.info(f"Syncing connection {conn_name=}")

        conn_id = api.create_or_update_connection(
            parent="ROOT",
            name=conn_name,
            protocol=conn_protocol,
            hostname=manifest["spec"]["hostname"],
            port=manifest["spec"]["port"]
        )

        expected_connections.add(conn_id)

        logging.info(f"Syncing connection users {conn_name=}")

        observed_connection_users = api.list_connection_users(conn_id=conn_id)

        for user in expected_users_by_manifest[manifest_name].values():
            if user["username"] not in observed_connection_users:
                api.create_user_connection(
                    username=user["username"],
                    conn_id=conn_id
                )

        for observed_user in observed_connection_users.values():
            if (observed_user["username"] not in expected_users_by_manifest[manifest_name]) and (observed_user["username"] != api.username):
                api.delete_user_connection(
                    username=observed_user["username"],
                    conn_id=conn_id
                )

    # Cull connections
    for observed_connection in observed_connections.values():
        if observed_connection["identifier"] not in expected_connections:
            api.delete_connection(conn_id=observed_connection["identifier"])
