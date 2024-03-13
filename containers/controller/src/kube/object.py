import asyncio
import logging
import secrets


class KubeObject:

    name: str
    manifest: dict
    task: asyncio.Future | None = None
    hash: str

    def __init__(
        self,
        name: str,
        manifest: dict
    ):
        self.name = name
        self.hash = secrets.token_hex(2)
        self.update(manifest=manifest)

    async def loop(self):
        logging.info(f"name={self.name}::{self.hash} loop")
        raise NotImplementedError()

    def update(self, manifest: dict):
        logging.info(f"name={self.name}::{self.hash} updating manifest {manifest=}")
        self.manifest = manifest

    async def run(self):
        logging.info(f"name={self.name}::{self.hash} creating task")
        self.task = asyncio.create_task(self.loop())

    async def cancel(self):
        logging.info(f"name={self.name}::{self.hash} cancelling")
        self.task.cancel()
        logging.info(f"name={self.name}::{self.hash} cancelled")
        await self.task
        logging.info(f"name={self.name}::{self.hash} halted")
