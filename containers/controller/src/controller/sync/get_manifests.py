import logging

from ..kube import kube_gather_objects


def get_manifests(namespace: str):

    logging.info("Searching for kubes manifests")
    manifests = kube_gather_objects(
        group="guacamole.ukserp.ac.uk",
        version="v1",
        plural="guacamoleconnections",
        namespace=namespace
    )
    logging.info(f"Found {len(manifests)} manifests")
    return manifests