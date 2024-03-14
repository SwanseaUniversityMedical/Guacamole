import asyncio
import logging
import secrets


class Resource:

    name: str
    interval: int
    manifest: dict
    interval_task: asyncio.Future | None = None
    task: asyncio.Future | None = None
    hash: str

    def __init__(
        self,
        name: str,
        manifest: dict
    ):
        self.name = name
        # Add a random hash to the name so that we can spot if we end up with
        # multiple tasks for the same resource.
        self.hash = secrets.token_hex(2)
        self.update(manifest=manifest)

    def __repr__(self):
        return f"{self.name}/{self.hash}"

    def interval(self) -> int:
        raise NotImplementedError()

    def sync(self):
        raise NotImplementedError()

    async def loop(self):
        logging.info(f"Loop {self}")
        while True:
            # Spawn a task to track the minimum amount of time to the next iteration and return immediately
            self.interval_task = asyncio.create_task(asyncio.sleep(self.interval()))
            # Call .sync() as a blocking function so that .update() can't run at the same time
            self.sync()
            # If sync was fast then wait the test of the interval otherwise loop immediately
            await self.interval_task
            self.interval_task = None

    def update(self, manifest: dict):
        logging.info(f"Update {self}")
        self.manifest = manifest
        # if self.interval_task is not None:
        #     self.interval_task.cancel()

    async def run(self):
        logging.info(f"Creating {self}")
        self.task = asyncio.create_task(self.loop())

    async def cancel(self):
        if self.task is not None:
            logging.info(f"Cancelling {self}")
            self.task.cancel()
            await self.task
            self.task = None

        # if self.interval_task is not None:
        #     logging.info(f"name={self.name}::{self.hash} cancelling interval")
        #     self.interval_task.cancel()