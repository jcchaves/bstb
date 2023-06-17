import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class OperationOrdersFetcher:
    def __init__(self, loop):
        self.submit_async(self.process(), loop)

    def submit_async(self, awaitable, loop):
        asyncio.run_coroutine_threadsafe(awaitable, loop)

    async def process(self):
        while True:
            logger.info("Consumiendo de api.....")
            await asyncio.sleep(10)
