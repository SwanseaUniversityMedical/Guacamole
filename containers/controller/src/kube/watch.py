import asyncio
import logging
import typing

import kubernetes_asyncio as k8s

from .object import KubeObject


async def kube_watch(
    namespace: str,
    factory: typing.Callable[..., KubeObject],
    **kwargs
):

    logging.info("connect to kubes api")
    k8s.config.load_incluster_config()

    resources = dict()
    resource_version = None

    try:

        while True:

            try:

                logging.info(f"watch kubes resource changes after {resource_version=}")
                async with k8s.client.ApiClient() as api:
                    crds = k8s.client.CustomObjectsApi(api)

                    async with k8s.watch.Watch().stream(
                        crds.list_namespaced_custom_object,
                        group="guacamole.ukserp.ac.uk",
                        version="v1",
                        namespace=namespace,
                        plural="guacamoleconnections",
                        send_initial_events=True,
                        resource_version_match="NotOlderThan",
                        resource_version=resource_version,
                        allow_watch_bookmarks=True
                    ) as stream:

                        # Consume the event stream forever
                        async for event in stream:

                            event_type = event["type"]
                            logging.info(f"{event_type=}")

                            manifest = event["object"]
                            metadata = manifest["metadata"]

                            name: str = "::".join([manifest["kind"], metadata["name"], metadata["namespace"]])
                            logging.info(f"{name=}")

                            resource_version = metadata["resourceVersion"]
                            logging.info(f"{resource_version=}")

                            if event_type == "ADDED":

                                logging.info(f"{name=} creating")

                                if name in resources:
                                    raise RuntimeError(
                                        ("ADDED event for resource already being monitored!", name, manifest, resources))

                                resources[name] = factory(name=name, manifest=manifest, **kwargs)
                                await resources[name].run()

                            elif event_type == "MODIFIED":

                                logging.info(f"{name=} updating")
                                resources[name].update(manifest=manifest)

                            elif event_type == "DELETED":

                                logging.info(f"{name=} cancelling")
                                try:
                                    await resources[name].cancel()
                                except asyncio.CancelledError:
                                    logging.info(f"{name=} cancelled")
                                finally:
                                    del resources[name]

                            else:
                                raise ValueError(("Unknown event type!", event))

            except k8s.client.exceptions.ApiException as ex:
                logging.exception(f"Exception raised!", exc_info=ex)

                if ex.status != 410:
                    logging.error("Exception is not (410 Gone)! Cancelling tasks and rethrowing!")
                    raise ex

                # Loops back to restarting the watch but keeps existing tasks alive
    finally:

        # Cancel running tasks
        for name in list(resources.keys()):
            logging.info(f"{name=} cancelling")
            try:
                await resources[name].cancel()
            except asyncio.CancelledError:
                logging.info(f"{name=} cancelled")
            finally:
                del resources[name]

    logging.info(f"halting watch")
