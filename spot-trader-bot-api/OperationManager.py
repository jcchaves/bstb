import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class OperationManager:
    def __init__(self, bncClient, operationOrdersFetcher, loop):
        self._operation = None
        self._orders_fetcher = operationOrdersFetcher
        self.submit_async(self.process(), loop)

    def submit_async(self, awaitable, loop):
        asyncio.run_coroutine_threadsafe(awaitable, loop)

    async def process(self):
        while True:
            logger.info("Operando.....")
            await asyncio.sleep(10)

    def createOperation(self, operation):
        operation["id"] = 123456
        self._operation = operation
        return operation

    def listOperations(self):
        if self._operation is not None:
            return {"operations": [self._operation]}
        return {"operations": []}
