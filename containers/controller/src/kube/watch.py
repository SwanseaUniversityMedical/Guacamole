import asyncio
import logging
import typing

import kubernetes_asyncio as k8s


from .resource import Resource


async def kube_watch(
    group: str,
    version: str,
    namespace: str,
    plural: str,
    factory: typing.Callable[..., Resource],
    **kwargs
):

    k8s.config.load_incluster_config()

    def resource_name(manifest: dict) -> str:
        metadata = manifest["metadata"]
        return "{kind}/{namespace}/{name}".format(
            kind=manifest["kind"],
            namespace=metadata["namespace"],
            name=metadata["name"]
        )

    # Dictionary to store all the running tasks so that we can update or cancel them later
    resources = dict()

    # Ensure all the resource tasks are cancelled before letting the exception propagate
    try:

        while True:

            # Catch k8s.client.exceptions.ApiException 410 Gone errors and restart the watch
            # Rethrow all other error codes and exception types
            try:

                logging.info(f"Watching resource changes")
                async with k8s.client.ApiClient() as api:
                    crds = k8s.client.api.CustomObjectsApi(api)

                    # List all current manifests
                    manifests = await crds.list_namespaced_custom_object(
                        group=group,
                        version=version,
                        namespace=namespace,
                        plural=plural,
                    )

                    # Convert the manifests into a dict keyed on resource name
                    manifests = {
                        resource_name(manifest): manifest
                        for manifest in manifests["items"]
                    }
                    logging.info(f"Discovered {len(manifests)} manifests")

                    # Synchronize the resources dict against the live manifests

                    # Cancel existing resources that are not found in the live manifests
                    for name in list(resources.keys()):

                        if name not in manifests:
                            # This will happen when the watcher restarts after a 410 Gone,
                            # and misses a DELETED event.
                            try:
                                await resources[name].cancel()
                            except asyncio.CancelledError:
                                pass
                            finally:
                                del resources[name]

                    # Create or update resources to match the live manifests
                    for name, manifest in manifests.items():

                        if name in resources:
                            # This will happen when the watcher restarts after a 410 Gone,
                            # and will only result in a change if there was a missed MODIFIED event
                            resources[name].update(manifest=manifest)

                        if name not in resources:
                            # This will happen on first run and when the watcher restarts after a 410 Gone,
                            # and misses an ADDED event
                            resources[name] = factory(name=name, manifest=manifest, **kwargs)
                            await resources[name].run()

                    # Start watching for changes to the live manifests
                    # If this errors out with a 410 Gone error then the
                    # surrounding try blocks will restart the watch
                    async with k8s.watch.Watch().stream(
                        crds.list_namespaced_custom_object,
                        group=group,
                        version=version,
                        namespace=namespace,
                        plural=plural,
                    ) as stream:

                        # Consume the event stream forever (or until 410 Gone error)
                        async for event in stream:

                            event_type = event["type"]
                            logging.info(f"Watcher event {event_type}")

                            manifest = event["object"]
                            name = resource_name(manifest)

                            if event_type in ["ADDED", "MODIFIED"]:

                                if name not in resources:
                                    # This will happen if the watcher sees new manifests being added
                                    resources[name] = factory(name=name, manifest=manifest, **kwargs)
                                    await resources[name].run()
                                else:
                                    # This will happen when the watcher starts because we pre-queried the live manifests
                                    # so ADDED events will actually be updates of already running resources.
                                    # It will also happen when MODIFIED events trigger naturally.
                                    # .update() is a blocking call which should force it to play nicely with a co-running
                                    # .sync() function being called from the async .loop() task.
                                    resources[name].update(manifest=manifest)

                            elif event_type == "DELETED":

                                # This will happen when the watcher sees a resource being deleted.
                                try:
                                    await resources[name].cancel()
                                except asyncio.CancelledError:
                                    pass
                                finally:
                                    del resources[name]

                            else:
                                raise ValueError(("Unknown event type!", event))

            except k8s.client.exceptions.ApiException as ex:

                if ex.status == 410:
                    logging.warning("Watcher restarting after (410 Gone) exception.")
                else:
                    logging.exception("Watcher exception is not (410 Gone)! Cancelling tasks and rethrowing!", exc_info=ex)
                    raise ex

                # Loops back to restarting the watch but keeps existing tasks alive
    finally:

        logging.info(f"Halting watcher")

        # Cancel running tasks
        for name in list(resources.keys()):
            try:
                await resources[name].cancel()
            except asyncio.CancelledError:
                pass
            finally:
                del resources[name]
