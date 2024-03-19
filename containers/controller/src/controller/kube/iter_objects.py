import logging

import kubernetes as k8s


def kube_object_name(manifest: dict) -> str:
    metadata = manifest["metadata"]
    return "{kind}/{namespace}/{name}".format(
        kind=manifest["kind"],
        namespace=metadata["namespace"],
        name=metadata["name"]
    )


def kube_iter_objects(
    group: str,
    version: str,
    namespace: str,
    plural: str,
):
    with k8s.client.ApiClient() as api:
        crds = k8s.client.api.CustomObjectsApi(api)

        # List all current manifests
        manifests = crds.list_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
        )

    yield from manifests["items"]


def kube_gather_objects(
    group: str,
    version: str,
    namespace: str,
    plural: str,
) -> dict:

    manifests = dict()

    for manifest in kube_iter_objects(
        group=group,
        version=version,
        namespace=namespace,
        plural=plural
    ):
        name = kube_object_name(manifest)

        if name in manifests:
            ex = ValueError(("Manifest with duplicate name!", name, manifest, manifests[name]))
            logging.exception("Manifest with duplicate name!", exc_info=ex)
            raise ex

        manifests[name] = manifest

    return manifests
