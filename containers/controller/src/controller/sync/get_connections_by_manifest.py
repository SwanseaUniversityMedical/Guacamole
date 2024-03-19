import logging


def get_connections_by_manifest(
    namespace: str,
    manifests: dict
):

    connections_by_manifest = dict()
    for name, manifest in manifests.items():

        logging.info(f"Searching connections for manifest {name}")

        # Currently yields a single connection based on a url in the crd
        # TODO Eventually should select pod services based on selectors in the crd.
        url = manifest["spec"]["url"]
        connections_by_manifest[name] = [url]

        logging.info(f"Found {len(connections_by_manifest[name])} connections")

    return connections_by_manifest
