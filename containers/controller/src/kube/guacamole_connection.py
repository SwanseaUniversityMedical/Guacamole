import asyncio
import logging


from .object import KubeObject

class GuacamoleConnection(KubeObject):

    async def loop(self):
        while True:
            logging.info(f"name={self.name}::{self.hash} loop")
            await asyncio.sleep(5)
